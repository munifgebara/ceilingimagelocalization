"""Avaliacao da precisao da localizacao (M4).

Cria um cenario sintetico reproduzivel: um local com uma planta e N fotos de
mapeamento em posicoes conhecidas (cada uma com um padrao visual distinto).
Depois, para cada posicao, gera uma foto de consulta (a mesma imagem com ruido e
variacao de brilho, simulando uma nova captura) e mede o erro de localizacao.

Metricas: erro mediano e medio (em unidades da planta e em metros, via escala) e
taxa de acerto dentro de um limiar.

Uso:
    pip install -e ".[dev]"            # precisa de httpx, numpy, pillow
    BASE_URL=http://localhost:8000 python avaliacao/avaliar.py --n 25

A API alvo precisa estar no ar (com banco). Gera docs/avaliacao/resultado.md.
"""

from __future__ import annotations

import argparse
import io
import math
import os
import statistics
from datetime import UTC, datetime
from pathlib import Path

import httpx
import numpy as np
from PIL import Image

BASE_URL = os.environ.get("BASE_URL", "http://localhost:8000")
# Cabecalho Host opcional (ex.: para bater no Ingress: HOST_HEADER=teto.local).
HOST_HEADER = os.environ.get("HOST_HEADER")
HEADERS = {"Host": HOST_HEADER} if HOST_HEADER else {}


def _png(arr: np.ndarray) -> bytes:
    buf = io.BytesIO()
    Image.fromarray(arr.astype(np.uint8), mode="L").save(buf, format="PNG")
    return buf.getvalue()


def imagem_base(seed: int) -> np.ndarray:
    """Padrao visual distinto e estavel por posicao."""
    rng = np.random.default_rng(seed)
    return (rng.random((96, 128)) * 255).astype(np.uint8)


def imagem_consulta(seed: int, sigma: float, brilho: float) -> bytes:
    """A imagem da posicao com ruido gaussiano e variacao de brilho."""
    base = imagem_base(seed).astype(np.float32)
    rng = np.random.default_rng(seed + 10_000)
    ruido = rng.normal(0, sigma, base.shape)
    return _png(np.clip(base + ruido + brilho, 0, 255))


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--n", type=int, default=25, help="numero de posicoes mapeadas")
    p.add_argument("--sigma", type=float, default=18.0, help="ruido na consulta")
    p.add_argument("--brilho", type=float, default=20.0, help="variacao de brilho na consulta")
    p.add_argument("--escala", type=float, default=0.05, help="metros por unidade da planta")
    p.add_argument("--limiar-m", type=float, default=2.0, help="limiar de acerto em metros")
    args = p.parse_args()

    cliente = httpx.Client(base_url=BASE_URL, headers=HEADERS, timeout=30)

    # 1) Local + planta sintetica (viewBox 1000x1000).
    local_id = cliente.post("/locais", json={"nome": "Avaliacao sintetica"}).json()["id"]
    svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000"></svg>'
    cliente.post(
        f"/locais/{local_id}/plantas",
        files={"arquivo": ("planta.svg", svg.encode(), "image/svg+xml")},
        data={"nome": "Terreo", "escala_m_por_unidade": str(args.escala)},
    )

    # 2) Mapeamento: N posicoes em grade.
    lado = math.ceil(math.sqrt(args.n))
    posicoes: list[tuple[int, float, float]] = []
    for i in range(args.n):
        x = (i % lado + 0.5) * (1000 / lado)
        y = (i // lado + 0.5) * (1000 / lado)
        posicoes.append((i, x, y))
        cliente.post(
            "/fotos",
            files={"imagem": (f"{i}.png", _png(imagem_base(i)), "image/png")},
            data={"local_id": local_id, "plan_x": str(x), "plan_y": str(y)},
        )

    # 3) Consulta + erro.
    erros_unidades: list[float] = []
    for seed, x, y in posicoes:
        consulta = imagem_consulta(seed, args.sigma, args.brilho)
        resp = cliente.post(
            "/localizar",
            files={"imagem": ("q.png", consulta, "image/png")},
            data={"local_id": local_id},
        ).json()
        if resp["x"] is None:
            continue
        erro = math.hypot(resp["x"] - x, resp["y"] - y)
        erros_unidades.append(erro)

    erros_m = [e * args.escala for e in erros_unidades]
    acertos = sum(1 for e in erros_m if e <= args.limiar_m)
    n = len(erros_m)

    relatorio = f"""# Resultado da avaliacao

Gerado em {datetime.now(UTC).isoformat(timespec="seconds")} (UTC).

## Cenario

- Backend de embedding: tiny-image (32x16, 512-d) — padrao do projeto.
- Posicoes mapeadas: **{args.n}** (grade {lado}x{lado} numa planta 1000x1000).
- Escala: **{args.escala} m/unidade** (ambiente de ~{1000 * args.escala:.0f} m).
- Consulta = imagem da posicao + ruido (sigma={args.sigma}) + brilho ({args.brilho:+.0f}).
- Limiar de acerto: **{args.limiar_m} m**.

## Metricas (n={n})

| Metrica | Unidades da planta | Metros |
|---|---|---|
| Erro mediano | {statistics.median(erros_unidades):.2f} | {statistics.median(erros_m):.3f} |
| Erro medio | {statistics.mean(erros_unidades):.2f} | {statistics.mean(erros_m):.3f} |
| Erro maximo | {max(erros_unidades):.2f} | {max(erros_m):.3f} |
| Taxa de acerto (<= {args.limiar_m} m) | — | {100 * acertos / n:.1f}% |

> Observacao: este e um cenario sintetico para validar o pipeline e o metodo de
> medicao. Com o backend de embedding forte (DINOv2, extra [ia]) e verificacao
> geometrica (OpenCV), espera-se erro menor em dados reais de teto.
"""

    saida = Path(__file__).resolve().parents[2] / "docs" / "avaliacao" / "resultado.md"
    saida.parent.mkdir(parents=True, exist_ok=True)
    saida.write_text(relatorio, encoding="utf-8")
    print(relatorio)
    print(f"Relatorio salvo em: {saida}")


if __name__ == "__main__":
    main()

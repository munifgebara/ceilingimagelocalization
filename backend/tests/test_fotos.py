"""Testes das rotas de fotos (M2)."""

import io

import numpy as np
from PIL import Image

from app.configuracao import obter_configuracao
from tests.conftest import requer_banco


def _imagem_png(cor: int = 128) -> bytes:
    """Gera uma imagem PNG simples em memoria."""
    arr = np.full((48, 64), cor, dtype=np.uint8)
    arr[10:30, 20:40] = 255  # um retangulo claro, para dar textura
    buf = io.BytesIO()
    Image.fromarray(arr, mode="L").save(buf, format="PNG")
    return buf.getvalue()


def _criar_local(cliente) -> str:
    return cliente.post("/locais", json={"nome": "Local Foto"}).json()["id"]


@requer_banco
def test_enviar_foto_gera_embedding(cliente):
    local_id = _criar_local(cliente)
    resp = cliente.post(
        "/fotos",
        files={"imagem": ("teto.png", _imagem_png(), "image/png")},
        data={
            "local_id": local_id,
            "latitude": "-23.5",
            "longitude": "-46.6",
            "gps_precisao": "12",
            "plan_x": "100",
            "plan_y": "200",
        },
    )
    assert resp.status_code == 201, resp.text
    foto = resp.json()
    assert foto["tipo"] == "mapeamento"
    assert foto["plan_x"] == 100

    # A imagem fica acessivel.
    img = cliente.get(f"/fotos/{foto['id']}/imagem")
    assert img.status_code == 200

    # Aparece na listagem do local.
    lista = cliente.get(f"/locais/{local_id}/fotos").json()
    assert len(lista) == 1


@requer_banco
def test_enviar_foto_local_inexistente(cliente):
    resp = cliente.post(
        "/fotos",
        files={"imagem": ("teto.png", _imagem_png(), "image/png")},
        data={"local_id": "00000000-0000-0000-0000-000000000000"},
    )
    assert resp.status_code == 404


def test_dimensao_do_embedding_bate_com_config():
    from app.visao.embeddings import DIMENSAO, gerar_embedding

    assert DIMENSAO == obter_configuracao().dimensao_embedding
    emb = gerar_embedding(_imagem_png())
    assert len(emb) == DIMENSAO

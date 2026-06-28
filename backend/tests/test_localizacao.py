"""Testes do pipeline de localizacao (M3)."""

import io

import numpy as np
from PIL import Image

from tests.conftest import requer_banco

# Dois pontos GPS bem distantes (~15 km) para testar o filtro por raio.
GPS_A = (-23.50, -46.60)
GPS_B = (-23.40, -46.50)


def _imagem(padrao: str) -> bytes:
    arr = np.zeros((48, 64), dtype=np.uint8)
    if padrao == "A":
        arr[5:20, 5:25] = 255  # claro no canto superior esquerdo
    else:
        arr[:] = 255
        arr[28:44, 40:60] = 0  # escuro no canto inferior direito
    buf = io.BytesIO()
    Image.fromarray(arr, mode="L").save(buf, format="PNG")
    return buf.getvalue()


def _criar_local(cliente) -> str:
    return cliente.post("/locais", json={"nome": "Local Loc"}).json()["id"]


def _mapear(cliente, local_id, padrao, gps, plan):
    cliente.post(
        "/fotos",
        files={"imagem": (f"{padrao}.png", _imagem(padrao), "image/png")},
        data={
            "local_id": local_id,
            "latitude": str(gps[0]),
            "longitude": str(gps[1]),
            "gps_precisao": "10",
            "plan_x": str(plan[0]),
            "plan_y": str(plan[1]),
        },
    )


@requer_banco
def test_localiza_pela_imagem_sem_gps(cliente):
    local_id = _criar_local(cliente)
    _mapear(cliente, local_id, "A", GPS_A, (10, 10))
    _mapear(cliente, local_id, "B", GPS_B, (500, 500))

    resp = cliente.post(
        "/localizar",
        files={"imagem": ("q.png", _imagem("A"), "image/png")},
    )
    assert resp.status_code == 200, resp.text
    dados = resp.json()
    # Deve cair perto do ponto A.
    assert dados["x"] < 100 and dados["y"] < 100
    assert dados["confianca"] > 0.9
    assert dados["candidatos"]


@requer_banco
def test_filtro_gps_restringe_candidatos(cliente):
    local_id = _criar_local(cliente)
    _mapear(cliente, local_id, "A", GPS_A, (10, 10))
    _mapear(cliente, local_id, "B", GPS_B, (500, 500))

    # Imagem da consulta e a A, mas o GPS aponta para perto de B (raio pequeno).
    resp = cliente.post(
        "/localizar",
        files={"imagem": ("q.png", _imagem("A"), "image/png")},
        data={"latitude": str(GPS_B[0]), "longitude": str(GPS_B[1]), "raio_m": "50"},
    )
    assert resp.status_code == 200
    dados = resp.json()
    # So o B esta dentro do raio, entao a posicao vem do B.
    assert len(dados["candidatos"]) == 1
    assert dados["x"] == 500 and dados["y"] == 500


@requer_banco
def test_sem_candidatos_retorna_vazio(cliente):
    local_id = _criar_local(cliente)
    resp = cliente.post(
        "/localizar",
        files={"imagem": ("q.png", _imagem("A"), "image/png")},
        data={"local_id": local_id},
    )
    assert resp.status_code == 200
    dados = resp.json()
    assert dados["x"] is None and dados["confianca"] == 0.0

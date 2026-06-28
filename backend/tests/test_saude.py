"""Testes do endpoint de saude e da raiz."""

from fastapi.testclient import TestClient

from app.principal import app

cliente = TestClient(app)


def test_raiz_responde():
    resposta = cliente.get("/")
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["projeto"]
    assert corpo["versao"]


def test_saude_responde_ok():
    resposta = cliente.get("/saude")
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["status"] == "ok"
    # 'banco' pode ser 'ok' (com banco) ou 'indisponivel' (sem banco no ambiente de teste).
    assert corpo["banco"] in {"ok", "indisponivel"}

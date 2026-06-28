"""Testes das rotas de locais."""

from tests.conftest import requer_banco


@requer_banco
def test_criar_e_listar_local(cliente):
    resp = cliente.post("/locais", json={"nome": "Shopping Centro", "descricao": "Teste"})
    assert resp.status_code == 201
    criado = resp.json()
    assert criado["nome"] == "Shopping Centro"
    assert criado["id"]

    lista = cliente.get("/locais").json()
    assert any(item["id"] == criado["id"] for item in lista)

    obtido = cliente.get(f"/locais/{criado['id']}")
    assert obtido.status_code == 200
    assert obtido.json()["nome"] == "Shopping Centro"


@requer_banco
def test_obter_local_inexistente(cliente):
    resp = cliente.get("/locais/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404


@requer_banco
def test_criar_local_sem_nome(cliente):
    resp = cliente.post("/locais", json={"descricao": "sem nome"})
    assert resp.status_code == 422

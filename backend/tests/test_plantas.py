"""Testes das rotas de plantas."""

from tests.conftest import requer_banco

SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600">'
    '<rect width="800" height="600" fill="#eee"/></svg>'
)


def _criar_local(cliente) -> str:
    return cliente.post("/locais", json={"nome": "Local X"}).json()["id"]


@requer_banco
def test_upload_e_obter_planta(cliente):
    local_id = _criar_local(cliente)
    resp = cliente.post(
        f"/locais/{local_id}/plantas",
        files={"arquivo": ("planta.svg", SVG.encode(), "image/svg+xml")},
        data={"nome": "Terreo", "escala_m_por_unidade": "0.05"},
    )
    assert resp.status_code == 201
    planta = resp.json()
    assert planta["nome"] == "Terreo"
    assert planta["largura"] == 800
    assert planta["altura"] == 600
    assert planta["escala_m_por_unidade"] == 0.05
    assert "<svg" in planta["svg"]

    lista = cliente.get(f"/locais/{local_id}/plantas").json()
    assert len(lista) == 1

    detalhe = cliente.get(f"/plantas/{planta['id']}")
    assert detalhe.status_code == 200
    assert "<svg" in detalhe.json()["svg"]


@requer_banco
def test_upload_arquivo_invalido(cliente):
    local_id = _criar_local(cliente)
    resp = cliente.post(
        f"/locais/{local_id}/plantas",
        files={"arquivo": ("x.txt", b"isto nao e svg", "text/plain")},
    )
    assert resp.status_code == 400


@requer_banco
def test_upload_planta_local_inexistente(cliente):
    resp = cliente.post(
        "/locais/00000000-0000-0000-0000-000000000000/plantas",
        files={"arquivo": ("planta.svg", SVG.encode(), "image/svg+xml")},
    )
    assert resp.status_code == 404

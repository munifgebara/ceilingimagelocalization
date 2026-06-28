"""Fixtures de teste.

Os testes que dependem do banco usam um Postgres real (com pgvector). Se o banco
nao estiver acessivel (ex.: ambiente local sem docker), esses testes sao pulados.
"""

import os
import tempfile

# Grava as imagens dos testes em um diretorio temporario (antes de importar a app,
# pois a configuracao e lida/cacheada na importacao).
os.environ.setdefault("DIRETORIO_FOTOS", tempfile.mkdtemp(prefix="teto-fotos-"))

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import text  # noqa: E402

import app.banco.modelos  # noqa: F401,E402 -- registra os modelos no metadata
from app.banco.sessao import Base, engine  # noqa: E402
from app.principal import app  # noqa: E402


def _banco_disponivel() -> bool:
    try:
        with engine.connect() as con:
            con.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


BANCO_OK = _banco_disponivel()

# Marcador para testes que exigem banco.
requer_banco = pytest.mark.skipif(not BANCO_OK, reason="Banco de dados indisponivel")


@pytest.fixture(scope="session", autouse=True)
def _esquema():
    """Cria extensoes e tabelas uma vez por sessao de teste."""
    if not BANCO_OK:
        yield
        return
    with engine.begin() as con:
        con.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        con.execute(text("CREATE EXTENSION IF NOT EXISTS cube"))
        con.execute(text("CREATE EXTENSION IF NOT EXISTS earthdistance"))
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture(autouse=True)
def _limpa_tabelas():
    """Limpa as tabelas depois de cada teste que usa banco."""
    yield
    if BANCO_OK:
        with engine.begin() as con:
            con.execute(text("TRUNCATE foto, planta, local RESTART IDENTITY CASCADE"))


@pytest.fixture
def cliente() -> TestClient:
    return TestClient(app)

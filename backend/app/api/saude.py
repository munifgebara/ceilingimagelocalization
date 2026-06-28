"""Endpoint de saude (healthcheck)."""

from fastapi import APIRouter
from sqlalchemy import text

from app import __version__
from app.api.dependencias import SessaoBanco
from app.esquemas import RespostaSaude

roteador = APIRouter()


@roteador.get("/saude", response_model=RespostaSaude, tags=["saude"])
def verificar_saude(sessao: SessaoBanco) -> RespostaSaude:
    """Verifica se a API esta de pe e se o banco responde."""
    try:
        sessao.execute(text("SELECT 1"))
        banco = "ok"
    except Exception:
        banco = "indisponivel"
    return RespostaSaude(status="ok", banco=banco, versao=__version__)

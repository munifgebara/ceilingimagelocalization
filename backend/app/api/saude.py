"""Endpoint de saude (healthcheck)."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app import __version__
from app.banco.sessao import obter_sessao
from app.esquemas import RespostaSaude

roteador = APIRouter()

# Sessao do banco injetada por requisicao.
SessaoBanco = Annotated[Session, Depends(obter_sessao)]


@roteador.get("/saude", response_model=RespostaSaude, tags=["saude"])
def verificar_saude(sessao: SessaoBanco) -> RespostaSaude:
    """Verifica se a API esta de pe e se o banco responde."""
    try:
        sessao.execute(text("SELECT 1"))
        banco = "ok"
    except Exception:
        banco = "indisponivel"
    return RespostaSaude(status="ok", banco=banco, versao=__version__)

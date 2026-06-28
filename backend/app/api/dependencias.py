"""Dependencias compartilhadas das rotas."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.banco.sessao import obter_sessao

# Sessao do banco injetada por requisicao.
SessaoBanco = Annotated[Session, Depends(obter_sessao)]

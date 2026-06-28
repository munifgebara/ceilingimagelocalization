"""Esquemas Pydantic de entrada/saida da API."""

from pydantic import BaseModel


class RespostaSaude(BaseModel):
    status: str
    banco: str
    versao: str

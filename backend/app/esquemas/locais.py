"""Esquemas de entrada/saida de locais."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class LocalCriar(BaseModel):
    nome: str = Field(min_length=1, max_length=200)
    descricao: str | None = None


class LocalLido(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    nome: str
    descricao: str | None
    criado_em: datetime

"""Esquemas de entrada/saida de plantas."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PlantaResumo(BaseModel):
    """Metadados da planta, sem o conteudo SVG (para listagens)."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    local_id: uuid.UUID
    nome: str
    largura: float | None
    altura: float | None
    escala_m_por_unidade: float | None
    criado_em: datetime


class PlantaLida(PlantaResumo):
    """Planta completa, incluindo o SVG."""

    svg: str

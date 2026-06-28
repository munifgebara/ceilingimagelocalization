"""Esquemas de entrada/saida de fotos."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class FotoLida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    local_id: uuid.UUID
    planta_id: uuid.UUID | None
    latitude: float | None
    longitude: float | None
    gps_precisao: float | None
    plan_x: float | None
    plan_y: float | None
    tipo: str
    criado_em: datetime

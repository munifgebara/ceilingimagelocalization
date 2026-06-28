"""Esquemas da localizacao (consulta)."""

from __future__ import annotations

import uuid

from pydantic import BaseModel


class CandidatoLido(BaseModel):
    foto_id: uuid.UUID
    similaridade: float
    plan_x: float | None
    plan_y: float | None
    inliers: int | None = None


class RespostaLocalizacao(BaseModel):
    x: float | None
    y: float | None
    confianca: float
    planta_id: uuid.UUID | None
    candidatos: list[CandidatoLido]

"""Modelos ORM: local, planta e foto."""

from __future__ import annotations

import uuid
from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, Float, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.banco.sessao import Base
from app.configuracao import obter_configuracao

_DIM = obter_configuracao().dimensao_embedding


def _novo_id() -> uuid.UUID:
    return uuid.uuid4()


class Local(Base):
    """Um ambiente mapeado (shopping, aeroporto, hospital...)."""

    __tablename__ = "local"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_novo_id)
    nome: Mapped[str] = mapped_column(String(200), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    plantas: Mapped[list[Planta]] = relationship(
        back_populates="local", cascade="all, delete-orphan"
    )
    fotos: Mapped[list[Foto]] = relationship(back_populates="local", cascade="all, delete-orphan")


class Planta(Base):
    """Planta baixa (SVG) vinculada a um local."""

    __tablename__ = "planta"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_novo_id)
    local_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("local.id", ondelete="CASCADE"))
    nome: Mapped[str] = mapped_column(String(200), nullable=False, default="Pavimento")
    svg: Mapped[str] = mapped_column(Text, nullable=False)
    largura: Mapped[float | None] = mapped_column(Float)
    altura: Mapped[float | None] = mapped_column(Float)
    # Quantos metros do mundo real equivalem a 1 unidade da planta (para estimar erro).
    escala_m_por_unidade: Mapped[float | None] = mapped_column(Float)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    local: Mapped[Local] = relationship(back_populates="plantas")
    fotos: Mapped[list[Foto]] = relationship(back_populates="planta")


class Foto(Base):
    """Foto do teto: de mapeamento (com posicao conhecida) ou de consulta."""

    __tablename__ = "foto"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_novo_id)
    local_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("local.id", ondelete="CASCADE"))
    planta_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("planta.id", ondelete="SET NULL")
    )

    imagem_url: Mapped[str | None] = mapped_column(Text)

    # GPS bruto capturado no momento da foto.
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)
    gps_precisao: Mapped[float | None] = mapped_column(Float)

    # Posicao marcada sobre a planta (so para fotos de mapeamento).
    plan_x: Mapped[float | None] = mapped_column(Float)
    plan_y: Mapped[float | None] = mapped_column(Float)

    # Embedding visual (pgvector).
    embedding: Mapped[list[float] | None] = mapped_column(Vector(_DIM))

    # 'mapeamento' (referencia) ou 'consulta'.
    tipo: Mapped[str] = mapped_column(String(20), nullable=False, default="mapeamento")

    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    local: Mapped[Local] = relationship(back_populates="fotos")
    planta: Mapped[Planta | None] = relationship(back_populates="fotos")

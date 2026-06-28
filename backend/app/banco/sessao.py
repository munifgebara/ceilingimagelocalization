"""Criacao da engine e das sessoes do SQLAlchemy."""

from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.configuracao import obter_configuracao

_config = obter_configuracao()

engine = create_engine(_config.banco_url, pool_pre_ping=True, future=True)
CriadorDeSessao = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    """Classe base de todos os modelos ORM."""


def obter_sessao() -> Iterator[Session]:
    """Dependencia do FastAPI: fornece uma sessao por requisicao."""
    sessao = CriadorDeSessao()
    try:
        yield sessao
    finally:
        sessao.close()

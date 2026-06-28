"""Configuracoes da aplicacao, lidas de variaveis de ambiente."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Configuracao(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # URL de conexao com o banco (SQLAlchemy + psycopg).
    banco_url: str = "postgresql+psycopg://teto:teto@localhost:5432/teto"

    # Ambiente: desenvolvimento | producao.
    ambiente: str = "desenvolvimento"

    # Dimensao dos embeddings de imagem (definida pelo modelo de visao).
    dimensao_embedding: int = 512

    # Filtro geografico: raio padrao (metros) ao buscar fotos candidatas por GPS.
    raio_gps_padrao_m: int = 50

    # Quantidade de candidatos retornados pela busca por similaridade.
    candidatos_topn: int = 20


@lru_cache
def obter_configuracao() -> Configuracao:
    """Retorna a configuracao (cacheada)."""
    return Configuracao()

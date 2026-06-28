"""Armazenamento das imagens das fotos em disco."""

from __future__ import annotations

import uuid
from pathlib import Path

from app.configuracao import obter_configuracao


def _diretorio() -> Path:
    caminho = Path(obter_configuracao().diretorio_fotos)
    caminho.mkdir(parents=True, exist_ok=True)
    return caminho


def salvar_imagem(foto_id: uuid.UUID, conteudo: bytes) -> str:
    """Grava a imagem e retorna o caminho relativo armazenado."""
    destino = _diretorio() / f"{foto_id}.jpg"
    destino.write_bytes(conteudo)
    return str(destino)


def ler_imagem(caminho: str) -> bytes:
    """Le os bytes de uma imagem armazenada."""
    return Path(caminho).read_bytes()

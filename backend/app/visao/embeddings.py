"""Geracao de embeddings de imagem do teto.

Backend padrao: "tiny-image" — converte a imagem para tons de cinza, reduz para
32x16 (512 pixels), achata e normaliza (subtrai a media e divide pela norma L2).
E um descritor global leve (sem torch), suficiente para habilitar o pipeline
ponta a ponta. Um backend forte (DINOv2) pode ser plugado depois (extra [ia]).

A dimensao resultante (512) deve bater com configuracao.dimensao_embedding e com
a coluna vector(512) do banco.
"""

from __future__ import annotations

import io

import numpy as np
from PIL import Image

# 32 x 16 = 512 valores.
_LARGURA = 32
_ALTURA = 16
DIMENSAO = _LARGURA * _ALTURA


def gerar_embedding(imagem_bytes: bytes) -> list[float]:
    """Recebe os bytes de uma imagem e retorna seu embedding (lista de floats)."""
    with Image.open(io.BytesIO(imagem_bytes)) as img:
        cinza = img.convert("L").resize((_LARGURA, _ALTURA))
    vetor = np.asarray(cinza, dtype=np.float32).flatten()
    vetor -= vetor.mean()  # invariancia a brilho
    norma = float(np.linalg.norm(vetor))
    if norma > 0:
        vetor /= norma
    return vetor.tolist()

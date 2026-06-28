"""Geracao de embeddings de imagem do teto.

Esboco da interface. A implementacao real (M2) usara um modelo de visao
(ex.: DINOv2 ou NetVLAD) para transformar a imagem em um vetor.
"""

from __future__ import annotations


def gerar_embedding(imagem_bytes: bytes) -> list[float]:
    """Recebe os bytes de uma imagem e retorna seu embedding.

    A implementar no M2 (depende das dependencias opcionais `[ia]`).
    """
    raise NotImplementedError("Geracao de embedding sera implementada no marco M2.")

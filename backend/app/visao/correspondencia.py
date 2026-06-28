"""Verificacao geometrica entre duas imagens do teto.

Esboco da interface. Implementacao real (M3): extrai features locais
(SuperPoint/SIFT), casa os pontos e aplica RANSAC, retornando o numero de
inliers como medida de confianca do casamento.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ResultadoCorrespondencia:
    inliers: int
    confianca: float


def verificar(consulta_bytes: bytes, referencia_bytes: bytes) -> ResultadoCorrespondencia:
    """Confirma geometricamente se duas fotos sao do mesmo ponto do teto.

    A implementar no M3.
    """
    raise NotImplementedError("Verificacao geometrica sera implementada no marco M3.")

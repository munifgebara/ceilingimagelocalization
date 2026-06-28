"""Verificacao geometrica entre duas imagens do teto.

Confirma se duas fotos sao do mesmo ponto do teto casando features locais e
aplicando RANSAC; retorna o numero de inliers como medida de confianca.

Usa OpenCV (extra [ia]). Se o OpenCV nao estiver instalado, `verificar` retorna
None e o pipeline cai para o ranqueamento apenas por embedding.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ResultadoCorrespondencia:
    inliers: int
    confianca: float


def opencv_disponivel() -> bool:
    try:
        import cv2  # noqa: F401

        return True
    except Exception:
        return False


def verificar(consulta_bytes: bytes, referencia_bytes: bytes) -> ResultadoCorrespondencia | None:
    """Confirma geometricamente se duas fotos sao do mesmo ponto do teto.

    Retorna None se o OpenCV nao estiver disponivel.
    """
    try:
        import cv2
        import numpy as np
    except Exception:
        return None

    def _carregar(b: bytes):
        arr = np.frombuffer(b, dtype=np.uint8)
        return cv2.imdecode(arr, cv2.IMREAD_GRAYSCALE)

    img1, img2 = _carregar(consulta_bytes), _carregar(referencia_bytes)
    if img1 is None or img2 is None:
        return None

    orb = cv2.ORB_create(nfeatures=1000)
    k1, d1 = orb.detectAndCompute(img1, None)
    k2, d2 = orb.detectAndCompute(img2, None)
    if d1 is None or d2 is None or len(k1) < 8 or len(k2) < 8:
        return ResultadoCorrespondencia(inliers=0, confianca=0.0)

    bf = cv2.BFMatcher(cv2.NORM_HAMMING)
    pares = bf.knnMatch(d1, d2, k=2)
    bons = [m for m, n in (p for p in pares if len(p) == 2) if m.distance < 0.75 * n.distance]
    if len(bons) < 8:
        return ResultadoCorrespondencia(inliers=len(bons), confianca=0.0)

    origem = np.float32([k1[m.queryIdx].pt for m in bons]).reshape(-1, 1, 2)
    destino = np.float32([k2[m.trainIdx].pt for m in bons]).reshape(-1, 1, 2)
    _, mascara = cv2.findHomography(origem, destino, cv2.RANSAC, 5.0)
    inliers = int(mascara.sum()) if mascara is not None else 0
    confianca = inliers / max(len(bons), 1)
    return ResultadoCorrespondencia(inliers=inliers, confianca=confianca)

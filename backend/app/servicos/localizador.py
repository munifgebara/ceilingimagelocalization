"""Pipeline de localizacao: filtro por GPS -> similaridade -> verificacao -> interpolacao."""

from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.banco.modelos import Foto
from app.configuracao import obter_configuracao
from app.esquemas.localizacao import CandidatoLido, RespostaLocalizacao
from app.servicos import armazenamento
from app.visao import correspondencia


def _buscar_candidatos(
    sessao: Session,
    embedding: list[float],
    latitude: float | None,
    longitude: float | None,
    raio_m: float | None,
    local_id: uuid.UUID | None,
    topn: int,
) -> list[tuple[Foto, float]]:
    """Retorna (foto, distancia_cosseno) dos melhores candidatos de mapeamento."""
    distancia = Foto.embedding.cosine_distance(embedding)
    stmt = select(Foto, distancia.label("distancia")).where(Foto.tipo == "mapeamento")

    if local_id is not None:
        stmt = stmt.where(Foto.local_id == local_id)

    # Filtro geografico por raio (earthdistance/cube), so se houver GPS.
    if latitude is not None and longitude is not None:
        centro = func.ll_to_earth(latitude, longitude)
        ponto = func.ll_to_earth(Foto.latitude, Foto.longitude)
        stmt = stmt.where(func.earth_box(centro, raio_m).op("@>")(ponto))
        stmt = stmt.where(func.earth_distance(centro, ponto) < raio_m)

    stmt = stmt.order_by(distancia).limit(topn)
    return list(sessao.execute(stmt).all())


def localizar(
    sessao: Session,
    imagem_bytes: bytes,
    embedding: list[float],
    latitude: float | None = None,
    longitude: float | None = None,
    gps_precisao: float | None = None,
    raio_m: float | None = None,
    local_id: uuid.UUID | None = None,
) -> RespostaLocalizacao:
    config = obter_configuracao()
    if raio_m is None:
        # Usa o maior entre o raio padrao e o dobro da imprecisao do GPS.
        raio_m = max(config.raio_gps_padrao_m, (gps_precisao or 0) * 2)

    achados = _buscar_candidatos(
        sessao, embedding, latitude, longitude, raio_m, local_id, config.candidatos_topn
    )

    candidatos: list[CandidatoLido] = []
    usar_opencv = correspondencia.opencv_disponivel()
    for foto, distancia in achados:
        similaridade = 1.0 - float(distancia)  # distancia de cosseno -> similaridade
        inliers = None
        if usar_opencv and foto.imagem_url:
            try:
                resultado = correspondencia.verificar(
                    imagem_bytes, armazenamento.ler_imagem(foto.imagem_url)
                )
                inliers = resultado.inliers if resultado else None
            except Exception:
                inliers = None
        candidatos.append(
            CandidatoLido(
                foto_id=foto.id,
                similaridade=round(similaridade, 4),
                plan_x=foto.plan_x,
                plan_y=foto.plan_y,
                inliers=inliers,
            )
        )

    # Mantem o vinculo foto->planta para interpolar (paralelo a 'candidatos').
    plantas = [foto.planta_id for foto, _ in achados]

    if not achados:
        return RespostaLocalizacao(x=None, y=None, confianca=0.0, planta_id=None, candidatos=[])

    # Reordena por inliers quando houver verificacao geometrica.
    if usar_opencv and any(c.inliers for c in candidatos):
        ordem = sorted(
            range(len(candidatos)),
            key=lambda i: (candidatos[i].inliers or 0, candidatos[i].similaridade),
            reverse=True,
        )
        candidatos = [candidatos[i] for i in ordem]
        plantas = [plantas[i] for i in ordem]

    planta_id = plantas[0]

    # Interpola (x, y) ponderando pelos candidatos validos da mesma planta.
    pesos_x = pesos_y = soma_pesos = 0.0
    for cand, p_id in zip(candidatos, plantas, strict=True):
        if cand.plan_x is None or cand.plan_y is None or p_id != planta_id:
            continue
        peso = max(cand.similaridade, 0.0) ** 2
        if cand.inliers:
            peso *= 1 + cand.inliers
        pesos_x += peso * cand.plan_x
        pesos_y += peso * cand.plan_y
        soma_pesos += peso

    x = pesos_x / soma_pesos if soma_pesos > 0 else None
    y = pesos_y / soma_pesos if soma_pesos > 0 else None
    confianca = round(max(candidatos[0].similaridade, 0.0), 4)

    return RespostaLocalizacao(
        x=x, y=y, confianca=confianca, planta_id=planta_id, candidatos=candidatos
    )

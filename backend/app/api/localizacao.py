"""Rota de localizacao (consulta)."""

import uuid
from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.api.dependencias import SessaoBanco
from app.esquemas.localizacao import RespostaLocalizacao
from app.servicos import localizador
from app.visao.embeddings import gerar_embedding

roteador = APIRouter(tags=["localizacao"])


@roteador.post("/localizar", response_model=RespostaLocalizacao)
async def localizar(
    sessao: SessaoBanco,
    imagem: Annotated[UploadFile, File()],
    latitude: Annotated[float | None, Form()] = None,
    longitude: Annotated[float | None, Form()] = None,
    gps_precisao: Annotated[float | None, Form()] = None,
    raio_m: Annotated[float | None, Form()] = None,
    local_id: Annotated[uuid.UUID | None, Form()] = None,
) -> RespostaLocalizacao:
    conteudo = await imagem.read()
    try:
        embedding = gerar_embedding(conteudo)
    except Exception as erro:
        raise HTTPException(status_code=400, detail=f"Imagem invalida: {erro}") from erro

    return localizador.localizar(
        sessao,
        imagem_bytes=conteudo,
        embedding=embedding,
        latitude=latitude,
        longitude=longitude,
        gps_precisao=gps_precisao,
        raio_m=raio_m,
        local_id=local_id,
    )

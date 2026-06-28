"""Rotas de fotos de mapeamento."""

import uuid
from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from fastapi.responses import Response

from app.api.dependencias import SessaoBanco
from app.banco.modelos import Foto, Local
from app.esquemas.fotos import FotoLida
from app.servicos import armazenamento
from app.visao.embeddings import gerar_embedding

roteador = APIRouter(tags=["fotos"])


@roteador.post("/fotos", response_model=FotoLida, status_code=status.HTTP_201_CREATED)
async def enviar_foto(
    sessao: SessaoBanco,
    imagem: Annotated[UploadFile, File()],
    local_id: Annotated[uuid.UUID, Form()],
    planta_id: Annotated[uuid.UUID | None, Form()] = None,
    latitude: Annotated[float | None, Form()] = None,
    longitude: Annotated[float | None, Form()] = None,
    gps_precisao: Annotated[float | None, Form()] = None,
    plan_x: Annotated[float | None, Form()] = None,
    plan_y: Annotated[float | None, Form()] = None,
    tipo: Annotated[str, Form()] = "mapeamento",
) -> Foto:
    if sessao.get(Local, local_id) is None:
        raise HTTPException(status_code=404, detail="Local nao encontrado")

    conteudo = await imagem.read()
    try:
        embedding = gerar_embedding(conteudo)
    except Exception as erro:
        raise HTTPException(status_code=400, detail=f"Imagem invalida: {erro}") from erro

    foto = Foto(
        local_id=local_id,
        planta_id=planta_id,
        latitude=latitude,
        longitude=longitude,
        gps_precisao=gps_precisao,
        plan_x=plan_x,
        plan_y=plan_y,
        tipo=tipo,
        embedding=embedding,
    )
    sessao.add(foto)
    sessao.flush()  # gera o id antes de salvar a imagem
    foto.imagem_url = armazenamento.salvar_imagem(foto.id, conteudo)
    sessao.commit()
    sessao.refresh(foto)
    return foto


@roteador.get("/locais/{local_id}/fotos", response_model=list[FotoLida])
def listar_fotos(local_id: uuid.UUID, sessao: SessaoBanco) -> list[Foto]:
    return list(sessao.query(Foto).filter(Foto.local_id == local_id))


@roteador.get("/fotos/{foto_id}/imagem")
def obter_imagem(foto_id: uuid.UUID, sessao: SessaoBanco) -> Response:
    foto = sessao.get(Foto, foto_id)
    if foto is None or not foto.imagem_url:
        raise HTTPException(status_code=404, detail="Imagem nao encontrada")
    return Response(content=armazenamento.ler_imagem(foto.imagem_url), media_type="image/jpeg")

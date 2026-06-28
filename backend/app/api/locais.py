"""Rotas de locais."""

import uuid

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.api.dependencias import SessaoBanco
from app.banco.modelos import Local
from app.esquemas.locais import LocalCriar, LocalLido

roteador = APIRouter(prefix="/locais", tags=["locais"])


@roteador.post("", response_model=LocalLido, status_code=status.HTTP_201_CREATED)
def criar_local(dados: LocalCriar, sessao: SessaoBanco) -> Local:
    local = Local(nome=dados.nome, descricao=dados.descricao)
    sessao.add(local)
    sessao.commit()
    sessao.refresh(local)
    return local


@roteador.get("", response_model=list[LocalLido])
def listar_locais(sessao: SessaoBanco) -> list[Local]:
    return list(sessao.scalars(select(Local).order_by(Local.criado_em.desc())))


@roteador.get("/{local_id}", response_model=LocalLido)
def obter_local(local_id: uuid.UUID, sessao: SessaoBanco) -> Local:
    local = sessao.get(Local, local_id)
    if local is None:
        raise HTTPException(status_code=404, detail="Local nao encontrado")
    return local

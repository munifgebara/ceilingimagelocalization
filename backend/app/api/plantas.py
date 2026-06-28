"""Rotas de plantas baixas (upload e leitura de SVG)."""

import re
import uuid
from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from app.api.dependencias import SessaoBanco
from app.banco.modelos import Local, Planta
from app.esquemas.plantas import PlantaLida, PlantaResumo

roteador = APIRouter(tags=["plantas"])


def _extrair_dimensoes(svg: str) -> tuple[float | None, float | None]:
    """Tenta extrair largura/altura do SVG (viewBox tem prioridade)."""
    m = re.search(r'viewBox\s*=\s*["\']\s*[\d.+-]+\s+[\d.+-]+\s+([\d.+-]+)\s+([\d.+-]+)', svg)
    if m:
        return float(m.group(1)), float(m.group(2))
    largura = re.search(r'\bwidth\s*=\s*["\']([\d.]+)', svg)
    altura = re.search(r'\bheight\s*=\s*["\']([\d.]+)', svg)
    return (
        float(largura.group(1)) if largura else None,
        float(altura.group(1)) if altura else None,
    )


@roteador.post(
    "/locais/{local_id}/plantas",
    response_model=PlantaLida,
    status_code=status.HTTP_201_CREATED,
)
async def enviar_planta(
    local_id: uuid.UUID,
    sessao: SessaoBanco,
    arquivo: Annotated[UploadFile, File()],
    nome: Annotated[str, Form()] = "Pavimento",
    escala_m_por_unidade: Annotated[float | None, Form()] = None,
) -> Planta:
    if sessao.get(Local, local_id) is None:
        raise HTTPException(status_code=404, detail="Local nao encontrado")

    conteudo = (await arquivo.read()).decode("utf-8", errors="replace")
    if "<svg" not in conteudo.lower():
        raise HTTPException(
            status_code=400,
            detail="Arquivo nao parece ser um SVG valido. (DWG sera convertido em versao futura.)",
        )

    largura, altura = _extrair_dimensoes(conteudo)
    planta = Planta(
        local_id=local_id,
        nome=nome,
        svg=conteudo,
        largura=largura,
        altura=altura,
        escala_m_por_unidade=escala_m_por_unidade,
    )
    sessao.add(planta)
    sessao.commit()
    sessao.refresh(planta)
    return planta


@roteador.get("/locais/{local_id}/plantas", response_model=list[PlantaResumo])
def listar_plantas(local_id: uuid.UUID, sessao: SessaoBanco) -> list[Planta]:
    if sessao.get(Local, local_id) is None:
        raise HTTPException(status_code=404, detail="Local nao encontrado")
    return list(sessao.query(Planta).filter(Planta.local_id == local_id))


@roteador.get("/plantas/{planta_id}", response_model=PlantaLida)
def obter_planta(planta_id: uuid.UUID, sessao: SessaoBanco) -> Planta:
    planta = sessao.get(Planta, planta_id)
    if planta is None:
        raise HTTPException(status_code=404, detail="Planta nao encontrada")
    return planta

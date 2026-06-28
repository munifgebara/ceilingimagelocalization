"""Ponto de entrada da API FastAPI."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.api import locais, plantas, saude

app = FastAPI(
    title="Localizacao Indoor por Imagens do Teto",
    description="API que estima a posicao na planta baixa a partir de uma foto do teto + GPS.",
    version=__version__,
)

# Os apps web (admin, coletor, teste) sao PWAs em outras origens.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(saude.roteador)
app.include_router(locais.roteador)
app.include_router(plantas.roteador)


@app.get("/", tags=["raiz"])
def raiz() -> dict:
    return {
        "projeto": "Localizacao Indoor por Imagens do Teto",
        "versao": __version__,
        "docs": "/docs",
    }

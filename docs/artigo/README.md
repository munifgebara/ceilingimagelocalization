# Artigo do projeto

Artigo científico em **duas colunas** (estilo conferência), em português:
resumo, introdução, trabalhos relacionados, **formalização matemática** do método,
arquitetura, implementação, avaliação experimental e trabalhos futuros — com
**figuras/esquemas** (arquitetura, fases, pipeline, modelo de dados, gráfico de
erro) e **referências**.

- **`Localizacao-Indoor-Teto.pdf`** — o artigo (gerado).
- **`gerar_artigo.py`** — gerador reproduzível (reportlab).
- **`dados_avaliacao.json`** — dados de erro por posição usados na Figura 5,
  produzidos por `backend/avaliacao/avaliar.py --saida-json`.

## Regerar

```bash
pip install reportlab

# (Opcional) Regerar os dados do gráfico — exige a API no ar:
BASE_URL=http://localhost:8000 \
  python backend/avaliacao/avaliar.py --n 25 \
  --saida-json docs/artigo/dados_avaliacao.json

# Gerar o PDF:
python docs/artigo/gerar_artigo.py
```

Ao mudar decisões importantes (arquitetura, métricas), atualize o script/dados e
regenere o PDF. O resumo das métricas também fica em
[`../avaliacao/resultado.md`](../avaliacao/resultado.md).

# Artigo do projeto

- **`Localizacao-Indoor-Teto.pdf`** — artigo técnico (português) descrevendo o
  problema, a hipótese, a arquitetura/método, a implementação, a avaliação
  teórica (cenário sintético) com resultados e os trabalhos futuros.
- **`gerar_artigo.py`** — gera o PDF de forma reproduzível.

## Regerar

```bash
pip install reportlab
python docs/artigo/gerar_artigo.py
```

Ao mudar decisões importantes (arquitetura, métricas), atualize o script e
regenere o PDF. Os números da avaliação vêm de
[`../avaliacao/resultado.md`](../avaliacao/resultado.md).

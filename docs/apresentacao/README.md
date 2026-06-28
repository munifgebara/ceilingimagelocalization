# Apresentação do projeto

- **`Localizacao-Indoor-Teto.pptx`** — apresentação pronta (abra no PowerPoint,
  LibreOffice Impress ou Google Slides).
- **`gerar_apresentacao.py`** — script que gera o PPTX de forma reproduzível.

## Regerar

```bash
pip install python-pptx
python docs/apresentacao/gerar_apresentacao.py
```

O conteúdo dos slides reflete a arquitetura descrita em
[`../../ARCHITECTURE.md`](../../ARCHITECTURE.md). Ao mudar decisões importantes,
atualize o script e regenere o `.pptx`.

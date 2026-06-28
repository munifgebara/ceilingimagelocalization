# Avaliação da precisão (M4)

Script reproduzível que mede o erro de localização do sistema.

## O que faz

1. Cria um local + planta sintética (1000×1000) com uma escala em metros/unidade.
2. Mapeia **N** fotos em posições conhecidas (cada uma com um padrão visual único).
3. Para cada posição, gera uma foto de **consulta** (mesma imagem + ruído + variação
   de brilho) e chama `/localizar`.
4. Calcula o erro (distância entre a posição estimada e a verdadeira) em unidades
   da planta e em metros, além da taxa de acerto dentro de um limiar.

## Como rodar

A API precisa estar no ar (com banco). Exemplos:

```bash
# Contra a API local (docker compose up -d)
BASE_URL=http://localhost:8000 python avaliacao/avaliar.py --n 25

# Contra o deploy no gimli (via Ingress)
BASE_URL=http://192.168.0.99 HOST_HEADER=teto.local python avaliacao/avaliar.py --n 25
```

Parâmetros: `--n`, `--sigma` (ruído), `--brilho`, `--escala` (m/unidade),
`--limiar-m` (limiar de acerto).

O resultado é impresso e salvo em [`../../docs/avaliacao/resultado.md`](../../docs/avaliacao/resultado.md).

## Próximos passos (pesquisa)

- Comparar o backend `tiny-image` com um modelo forte (DINOv2/NetVLAD, extra `[ia]`).
- Ativar a verificação geométrica (OpenCV) e medir o ganho.
- Avaliar com **dados reais** de teto (fotos com posição verdadeira) e variar o
  raio de GPS, o `top-N` e os limiares de RANSAC.

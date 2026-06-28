# Resultado da avaliacao

Gerado em 2026-06-28T22:00:23+00:00 (UTC).

## Cenario

- Backend de embedding: tiny-image (32x16, 512-d) — padrao do projeto.
- Posicoes mapeadas: **25** (grade 5x5 numa planta 1000x1000).
- Escala: **0.05 m/unidade** (ambiente de ~50 m).
- Consulta = imagem da posicao + ruido (sigma=18.0) + brilho (+20).
- Limiar de acerto: **2.0 m**.

## Metricas (n=25)

| Metrica | Unidades da planta | Metros |
|---|---|---|
| Erro mediano | 11.90 | 0.595 |
| Erro medio | 10.76 | 0.538 |
| Erro maximo | 18.93 | 0.947 |
| Taxa de acerto (<= 2.0 m) | — | 100.0% |

> Observacao: este e um cenario sintetico para validar o pipeline e o metodo de
> medicao. Com o backend de embedding forte (DINOv2, extra [ia]) e verificacao
> geometrica (OpenCV), espera-se erro menor em dados reais de teto.

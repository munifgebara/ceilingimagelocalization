# Glossário

- **Embedding**: vetor numérico que representa o conteúdo visual de uma foto.
  Fotos parecidas têm embeddings próximos. Guardado com `pgvector`.
- **Visual Place Recognition (VPR)**: reconhecer "que lugar é este" a partir de
  uma imagem, comparando com uma base de referência.
- **Verificação geométrica**: confirmar um casamento entre duas imagens checando
  se os pontos correspondentes formam uma transformação geométrica coerente
  (usando features locais + RANSAC).
- **RANSAC**: algoritmo que separa correspondências boas (*inliers*) das ruins
  (*outliers*) ao estimar uma transformação robusta.
- **earthdistance / cube**: extensões do Postgres que permitem calcular distância
  geográfica e fazer busca por raio sem PostGIS.
- **pgvector**: extensão do Postgres para armazenar vetores e buscar por
  similaridade (cosseno, L2).
- **Planta baixa**: representação 2D do ambiente (em SVG no projeto).
- **plan_x / plan_y**: coordenadas de um ponto sobre a planta baixa.
- **Mapeamento**: fase de coleta de fotos de referência (com posição conhecida).
- **Consulta**: foto enviada para ser localizada.
- **PWA**: aplicação web instalável que acessa câmera e GPS pelo navegador.
- **gimli**: o servidor (192.168.0.99) onde o projeto roda (k3s/Kubernetes).

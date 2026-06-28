# Localização Indoor Baseada em Imagens do Teto

Projeto de pesquisa: estimar a posição de um usuário dentro de um ambiente
fechado (shopping, aeroporto, hospital) a partir de uma **foto do teto** + GPS
aproximado, retornando uma coordenada `(x, y)` sobre a planta baixa do local.

## Hipótese

O teto é uma referência visual estável (poucas pessoas, pouca mudança temporal,
iluminação consistente). Uma base de fotos do teto georreferenciadas na planta
permite localizar uma nova foto por reconhecimento visual. O GPS — impreciso
indoor — serve como **filtro grosseiro**, reduzindo o universo de milhares de
fotos para dezenas/centenas de candidatos antes do match visual fino.

## Decisões de arquitetura

| Tema            | Decisão                                                        |
|-----------------|---------------------------------------------------------------|
| Backend         | **Python + FastAPI**                                           |
| Match visual    | **Híbrido**: embeddings (retrieval) + verificação geométrica  |
| Banco           | **PostgreSQL + pgvector + earthdistance/cube** (sem PostGIS — ver nota) |
| Saída da API    | **Coordenada `(x,y)` interpolada na planta + confiança**      |
| Planta baixa    | **SVG canônico** (DWG convertido para SVG/DXF no upload)       |
| GPS ↔ planta    | **Fase 1**: GPS independente (só filtro) + `x,y` marcado manualmente. **Fase 2**: georreferenciar a planta com pontos de controle |
| Frontend        | **Vue 3 + Vite + PWA** (3 apps: admin, coletor, teste)        |
| MVP             | Fluxo fim-a-fim mínimo (vertical slice)                        |

### Nota sobre o filtro geográfico (sem PostGIS)

O Postgres compartilhado do cluster (`pgvector/pgvector:pg17`) **não tem PostGIS**,
mas tem as extensões `cube` e `earthdistance`. Como nosso uso de geografia é apenas
"selecionar os pontos dentro de um raio de um GPS", usamos:

- `ll_to_earth(lat, lon)` para projetar coordenadas em um ponto 3D (`cube`);
- índice **GiST** em `ll_to_earth(lat, lon)` para busca eficiente;
- `earth_box(centro, raio)` + `earth_distance(...)` para o filtro por raio.

Isso evita subir um segundo banco. Se no futuro precisarmos de geometria rica
(polígonos de lojas, recorte por área), avaliamos PostGIS em um banco dedicado
(Fase 2).

## Componentes

```
                          ┌─────────────────────────────┐
   App Admin (PWA) ──────▶│                             │
   - cadastra local       │      API FastAPI (Python)   │──┐
   - upload planta SVG     │  ┌───────────────────────┐  │  │
                          │  │ Vision service        │  │  │
   App Coletor (PWA) ────▶│  │ - embedding (DINOv2/   │  │  │
   - foto teto + GPS + xy  │  │   NetVLAD)            │  │  │
                          │  │ - features locais     │  │  │
   App Teste (PWA) ──────▶│  │   (SuperPoint+LightGlue│  │  │
   - foto + GPS → posição  │  │   ou SIFT) + RANSAC   │  │  │
                          │  └───────────────────────┘  │  │
                          └─────────────────────────────┘  │
                                                            ▼
                          ┌─────────────────────────────────────┐
                          │ PostgreSQL + pgvector + earthdistance│
                          │ - locais, plantas (SVG)              │
                          │ - fotos: lat/lon, xy, embedding      │
                          └─────────────────────────────────────┘
                          + storage de objetos (fotos originais)
```

## Pipeline de localização (query)

1. Recebe foto do teto + GPS (lat/lon, accuracy).
2. **Filtro geográfico** (earthdistance/cube): seleciona fotos de referência
   dentro de um raio do GPS (`earth_box` + `earth_distance`), ordenadas por
   distância. Universo → dezenas/centenas.
3. **Retrieval visual** (pgvector): calcula embedding da query e busca os top-N
   candidatos por similaridade de cosseno *dentro do conjunto filtrado*.
4. **Verificação geométrica**: extrai features locais e faz matching +
   RANSAC entre a query e cada candidato; descarta matches geometricamente
   inconsistentes e gera um score de confiança.
5. **Estimativa de posição**: interpola `(x,y)` na planta ponderando os
   candidatos válidos pelo score (ex.: média ponderada / triangulação).
6. Retorna `{ x, y, confidence, candidatos_usados }`.

## Modelo de dados (esboço)

```
location        (id, nome, descricao, criado_em)
floorplan       (id, location_id, svg, largura, altura, escala_m_por_unidade,
                 -- fase 2: pontos de controle p/ georreferência
                )
foto            (id, local_id, planta_id,
                 imagem_url,
                 latitude, longitude, gps_precisao,   -- GPS bruto
                 plan_x, plan_y,                       -- posição marcada na planta
                 embedding vector(D),                  -- pgvector
                 tipo  -- 'mapeamento' | 'consulta'
                 criado_em)
-- índices:
--   GiST em ll_to_earth(latitude, longitude)  -> filtro por raio (earthdistance/cube)
--   HNSW/IVFFlat em embedding (vector_cosine_ops) -> similaridade (pgvector)
```

## Os 3 apps web (PWA)

- **Admin**: cadastra locais, faz upload/visualização da planta (SVG), gerencia
  fotos e dispara reindexação.
- **Coletor**: tira foto do teto, captura GPS, e o usuário toca na planta para
  marcar onde a foto foi tirada (`x,y`). Envia tudo para a API.
- **Teste**: tira foto + GPS, chama a API de localização e mostra o ponto
  estimado na planta com o nível de confiança.

## Roadmap (MVP fim-a-fim primeiro)

- **M0 — Fundação**: monorepo, docker-compose (Postgres+PostGIS+pgvector),
  FastAPI esqueleto, migrações, healthcheck.
- **M1 — Cadastro**: API + app Admin para criar local e subir planta SVG.
- **M2 — Coleta**: app Coletor (câmera+GPS+marcação na planta) → grava foto,
  GPS, `x,y` e embedding.
- **M3 — Localização**: endpoint de query (filtro GPS → retrieval → verificação
  → interpolação) + app Teste mostrando o ponto na planta.
- **M4 — Avaliação**: métricas de precisão (erro em metros), dataset de teste,
  ajuste do modelo de embedding e parâmetros (raio GPS, N, thresholds).

## Pilha tecnológica (resumo)

- **Backend**: Python 3.12, FastAPI, SQLAlchemy + Alembic, Pydantic.
- **Visão/IA**: PyTorch, embeddings (DINOv2 ou NetVLAD), features locais
  (SuperPoint + LightGlue, fallback SIFT/OpenCV), pgvector para ANN.
- **Banco**: PostgreSQL 17 + pgvector + earthdistance/cube (Postgres compartilhado do cluster gimli).
- **Deploy**: Kubernetes (k3s) no servidor **gimli** (192.168.0.99), Ingress Traefik, exposição externa via **Cloudflare Tunnel**. CI/CD com **GitHub Actions self-hosted runner**.
- **Frontend**: Vue 3 + Vite + vite-plugin-pwa.
- **Infra**: Docker Compose para dev; storage de objetos (MinIO/local) p/ fotos.

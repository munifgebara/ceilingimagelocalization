---
name: banco-dados
description: Trabalha com o banco do projeto — migrações Alembic, extensões pgvector/earthdistance, e modelagem das tabelas (local, planta, foto). Use ao criar/alterar tabelas, escrever migrações ou consultas de similaridade/geográficas.
---

# Banco de dados

PostgreSQL 17 (`pgvector/pgvector:pg17`). Extensões usadas: **`vector`**
(embeddings), **`cube`** e **`earthdistance`** (filtro por raio de GPS).
**Não há PostGIS.**

## Migrações (Alembic)

```bash
cd backend
alembic revision -m "<descrição>"   # cria migração
alembic upgrade head                # aplica
alembic downgrade -1                # reverte uma
```

A migração inicial cria as extensões:
```sql
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS cube;
CREATE EXTENSION IF NOT EXISTS earthdistance;
```

## Modelo (resumo)

- `local` — o ambiente mapeado (shopping, etc.).
- `planta` — planta baixa em SVG vinculada a um `local`.
- `foto` — foto do teto: `latitude`, `longitude`, `gps_precisao`, `plan_x`,
  `plan_y`, `embedding vector(D)`, `tipo` (`mapeamento`/`consulta`).

## Índices importantes

```sql
-- Filtro por raio de GPS (earthdistance/cube)
CREATE INDEX idx_foto_geo ON foto USING gist (ll_to_earth(latitude, longitude));

-- Similaridade de embeddings (pgvector, cosseno)
CREATE INDEX idx_foto_embedding ON foto USING hnsw (embedding vector_cosine_ops);
```

## Consultas-chave

```sql
-- Candidatos dentro de um raio (metros) de um ponto GPS
SELECT * FROM foto
WHERE tipo = 'mapeamento'
  AND earth_box(ll_to_earth(:lat, :lon), :raio) @> ll_to_earth(latitude, longitude)
  AND earth_distance(ll_to_earth(:lat, :lon), ll_to_earth(latitude, longitude)) < :raio;

-- Top-N por similaridade visual (entre os candidatos)
SELECT id, embedding <=> :consulta AS distancia
FROM foto
ORDER BY embedding <=> :consulta
LIMIT :n;
```

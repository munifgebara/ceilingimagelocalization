# API (rascunho)

Base URL local: `http://localhost:8000`. Documentação interativa: `/docs`.

> Esta é a especificação-alvo. Os endpoints são implementados ao longo dos marcos
> M1–M3. O que já existe hoje (M0) é apenas `/saude`.

## Saúde

```
GET /saude
200 { "status": "ok", "banco": "ok", "versao": "0.1.0" }
```

## Locais (M1)

```
POST /locais            { "nome": "...", "descricao": "..." }  -> 201 local
GET  /locais            -> lista de locais
GET  /locais/{id}       -> local
```

## Plantas (M1)

```
POST /locais/{id}/plantas   (multipart: arquivo SVG/DWG, escala) -> 201 planta
GET  /plantas/{id}          -> metadados + SVG
```

## Fotos de mapeamento (M2)

```
POST /fotos   (multipart)
  imagem: arquivo
  local_id, planta_id
  latitude, longitude, gps_precisao
  plan_x, plan_y
  -> 201 { id, embedding_gerado: true }
```

## Localização / consulta (M3)

```
POST /localizar   (multipart)
  imagem: arquivo
  latitude, longitude, gps_precisao
  -> 200 {
       "x": 123.4, "y": 567.8,
       "confianca": 0.82,
       "planta_id": "...",
       "candidatos": [ { "foto_id": "...", "similaridade": 0.91, "inliers": 142 } ]
     }
```

Pipeline da consulta: filtro por raio de GPS (earthdistance) → top-N por
similaridade (pgvector) → verificação geométrica (features + RANSAC) →
interpolação ponderada de `(x, y)`. Ver [`../ARCHITECTURE.md`](../ARCHITECTURE.md).

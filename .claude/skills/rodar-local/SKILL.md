---
name: rodar-local
description: Sobe e testa o projeto no ambiente de desenvolvimento local (Postgres com pgvector + API FastAPI) via docker compose. Use quando pedirem para rodar, iniciar ou testar o projeto localmente.
---

# Rodar localmente

## Subir tudo

```bash
docker compose up -d --build      # ou: make subir
```

- API: http://localhost:8000
- Swagger (docs interativa): http://localhost:8000/docs
- Healthcheck: `curl http://localhost:8000/saude`

## Logs

```bash
docker compose logs -f api        # ou: make logs
```

## Testes e lint

```bash
make test
make lint
```

## Migrações

```bash
make migrar                       # alembic upgrade head
```

## Derrubar

```bash
docker compose down               # ou: make descer
# Apagar também os dados do banco:
docker compose down -v
```

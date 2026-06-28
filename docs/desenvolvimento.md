# Guia de desenvolvimento

## Pré-requisitos

- Docker + Docker Compose
- (Opcional, para rodar fora do Docker) Python 3.12+ e Node 20+

## Subir o ambiente local

```bash
make subir          # docker compose up -d --build
make logs           # acompanha a API
```

- API: http://localhost:8000
- Swagger: http://localhost:8000/docs
- Saúde: `curl http://localhost:8000/saude`

## Testes e estilo

```bash
make test           # pytest
make lint           # ruff check
make format         # ruff format
```

## Banco de dados

```bash
make migrar         # alembic upgrade head
```

Detalhes do modelo e das consultas em [`../.claude/skills/banco-dados/SKILL.md`](../.claude/skills/banco-dados/SKILL.md).

## Fluxo de trabalho

Toda mudança segue: **issue → branch → Pull Request → aprovação → merge na
`master`**. Nunca commite direto na `master`.

1. `gh issue create --title "..." --body "..."`
2. `git switch -c feat/<resumo>`
3. Commits pequenos em português; `make test && make lint`
4. `gh pr create --base master --body "Closes #N ..."`
5. `gh pr review --approve && gh pr merge --squash --delete-branch`

A skill `nova-tarefa` automatiza isso.

## Estrutura

```
backend/   API FastAPI + visão/IA
frontend/  Vue 3 + Vite (admin, coletor, teste) + compartilhado/
deploy/    Manifestos Kubernetes (gimli)
docs/      Documentação
```

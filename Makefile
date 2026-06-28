# Atalhos do projeto. Use `make ajuda` para ver os comandos.

.DEFAULT_GOAL := ajuda

.PHONY: ajuda subir descer logs test lint format migrar deploy-gimli

ajuda:  ## Mostra esta ajuda
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	 awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

subir:  ## Sobe o ambiente local (Postgres + API)
	docker compose up -d --build

descer:  ## Derruba o ambiente local
	docker compose down

logs:  ## Acompanha os logs da API
	docker compose logs -f api

test:  ## Roda os testes do backend
	cd backend && python -m pytest -q

lint:  ## Verifica o estilo do código backend
	cd backend && ruff check .

format:  ## Formata o código backend
	cd backend && ruff format .

migrar:  ## Aplica as migrações do banco
	cd backend && alembic upgrade head

deploy-gimli:  ## Faz o deploy no gimli (ver docs/deploy.md)
	bash deploy/scripts/deploy-gimli.sh

avaliar:  ## Roda a avaliacao de precisao (API precisa estar no ar)
	cd backend && python avaliacao/avaliar.py --n 25

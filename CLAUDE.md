# Instruções do projeto para o Claude Code

Este arquivo orienta o Claude Code ao trabalhar neste repositório. Leia antes de
qualquer tarefa.

## O projeto

**Localização Indoor Baseada em Imagens do Teto.** Uma API recebe uma foto do
teto + GPS aproximado e retorna a posição `(x, y)` na planta baixa do local.
Detalhes em [`ARCHITECTURE.md`](ARCHITECTURE.md).

## Idioma — IMPORTANTE

O **português é o idioma oficial** de tudo:

- Documentação, README, comentários.
- **Nomes de variáveis, funções, classes, módulos, tabelas e colunas em
  português.** Ex.: `local`, `planta`, `foto`, `latitude`, `gerar_embedding()`,
  `calcular_posicao()`.
- Mensagens de commit, títulos e descrições de issues e PRs em português.
- Termos técnicos consagrados em inglês são mantidos: *embedding*, *commit*,
  *deploy*, *endpoint*, *Pull Request*, *RANSAC*, etc.

## Fluxo de trabalho — OBRIGATÓRIO

Para **cada tarefa**:

1. **Crie uma issue no GitHub** descrevendo a tarefa (em português).
2. Crie um **branch** a partir da `master` (ex.: `feat/<resumo>` ou
   `fix/<resumo>`).
3. Faça o trabalho com commits pequenos e descritivos.
4. Abra um **Pull Request para a `master`** referenciando a issue
   (`Closes #N`).
5. **Aprove e faça o merge** do PR (squash). Nunca commite direto na `master`.

> Exceção única: o commit inicial de bootstrap do repositório foi direto na
> `master` (a primeira vez), porque não havia branch base. A partir daí, sempre
> via PR.

Há uma skill que automatiza isso: **`nova-tarefa`** (`.claude/skills/nova-tarefa`).

## Ambiente / Infra

- **Repositório remoto**: `https://github.com/munifgebara/ceilingimagelocalization`
  (branch base: `master`).
- **Servidor de deploy (gimli)**: `192.168.0.99`, acesso via `ssh munif@192.168.0.99`.
  - Kubernetes **k3s** (single node). `kubectl` exige `sudo` (`sudo -n kubectl ...`).
  - Ingress: **Traefik** (`ingressClassName: traefik`).
  - StorageClass padrão: `local-path`.
  - **Postgres compartilhado**: StatefulSet `postgres-0` no namespace `platform`,
    service `postgres.platform.svc.cluster.local:5432`, imagem
    `pgvector/pgvector:pg17`. Credenciais no secret `postgres-secret` (namespace
    `platform`). Tem `vector`, `cube`, `earthdistance` — **não tem PostGIS**.
  - Exposição externa via **Cloudflare Tunnel** (padrão `cloudflared` já usado por
    outros apps no namespace `platform`).
  - Existe um **GitHub Actions runner self-hosted** no gimli (usado pelo CI).
- **Namespace do projeto no cluster**: `teto`.

## Decisões técnicas fixadas

- Backend: **Python + FastAPI**. Banco: **PostgreSQL + pgvector + earthdistance**.
- Match visual: **híbrido** (embeddings + verificação geométrica).
- Saída da API: **`(x, y)` interpolado + confiança**.
- Planta baixa: **SVG canônico** (DWG convertido no upload).
- GPS↔planta: Fase 1 = GPS só como filtro + `x,y` manual.
- Frontend: **Vue 3 + Vite (PWA)**.

## Comandos úteis

```bash
# Dev local
docker compose up -d           # sobe Postgres + API
make test                      # roda os testes do backend

# Deploy / cluster (via SSH no gimli)
sudo -n kubectl get pods -n teto
```

Veja também [`docs/deploy.md`](docs/deploy.md) e [`docs/desenvolvimento.md`](docs/desenvolvimento.md).

## Estilo de código

- Backend Python: siga PEP 8, use type hints, formate com `ruff`/`black`.
  Nomes em português.
- Frontend Vue: componentes em SFC (`<script setup>`), nomes em português.
- Comentários explicam o "porquê", não o "o quê".

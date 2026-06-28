# Localização Indoor Baseada em Imagens do Teto

> Estime onde alguém está dentro de um ambiente fechado (shopping, aeroporto,
> hospital) a partir de uma **foto do teto** e um GPS aproximado, retornando uma
> coordenada `(x, y)` sobre a planta baixa do local.

[![CI](https://github.com/munifgebara/ceilingimagelocalization/actions/workflows/ci.yml/badge.svg)](https://github.com/munifgebara/ceilingimagelocalization/actions/workflows/ci.yml)

## Por que o teto?

O teto é uma referência visual **estável**: tem poucas pessoas passando, muda
pouco com o tempo e a iluminação é mais constante que no nível do chão. Isso o
torna muito mais confiável para reconhecimento visual de lugar (*visual place
recognition*) do que fotos tiradas na altura dos olhos.

## Como funciona (resumo)

1. **Mapeamento**: um coletor tira várias fotos do teto. A cada foto, o app
   captura o **GPS** e o usuário **toca na planta** para marcar onde a foto foi
   tirada (`x, y`). Cada foto vira um vetor (*embedding*) guardado no banco.
2. **Consulta**: o usuário envia uma nova foto do teto + GPS. A API:
   - filtra as fotos de referência por **raio de GPS** (reduz milhares → dezenas);
   - busca as mais **parecidas visualmente** (similaridade de *embeddings*);
   - **confirma a geometria** com casamento de pontos (features locais + RANSAC);
   - **interpola** a posição `(x, y)` na planta e devolve com um nível de confiança.

Veja os detalhes em [`ARCHITECTURE.md`](ARCHITECTURE.md).

## Componentes

| Componente | Descrição | Tecnologia |
|------------|-----------|------------|
| **API** | Recebe fotos, gera embeddings, faz o match e a localização | Python + FastAPI |
| **Banco** | Locais, plantas, fotos, embeddings e filtro geográfico | PostgreSQL + pgvector + earthdistance |
| **App Admin** | Cadastra locais e faz upload da planta (SVG) | Vue 3 + Vite (PWA) |
| **App Coletor** | Tira foto do teto, captura GPS e marca a posição na planta | Vue 3 + Vite (PWA) |
| **App Teste** | Envia foto + GPS e mostra a posição estimada na planta | Vue 3 + Vite (PWA) |

## Estrutura do repositório

```
.
├── backend/        # API FastAPI (Python) + visão computacional/IA
├── frontend/       # Apps web (Vue 3 + Vite, PWA): admin, coletor, teste
│   └── compartilhado/  # Código comum (câmera, GPS, cliente HTTP, planta SVG)
├── deploy/k8s/     # Manifestos Kubernetes (gimli / k3s)
├── docs/           # Documentação (em português)
├── .claude/        # Configuração e skills do Claude Code
├── ARCHITECTURE.md # Decisões de arquitetura
└── docker-compose.yml  # Ambiente de desenvolvimento local
```

## Começando (desenvolvimento local)

Pré-requisitos: Docker + Docker Compose.

```bash
# Sobe Postgres (pgvector) + API
docker compose up -d

# A API fica em http://localhost:8000
# Documentação interativa (Swagger): http://localhost:8000/docs
curl http://localhost:8000/saude
```

Mais detalhes em [`docs/desenvolvimento.md`](docs/desenvolvimento.md).

## Deploy

O deploy é feito no servidor **gimli** (k3s/Kubernetes), exposto à internet via
**Cloudflare Tunnel**. Veja [`docs/deploy.md`](docs/deploy.md).

## Fluxo de trabalho (contribuição)

Toda mudança segue o fluxo: **issue → branch → Pull Request → aprovação → merge
em `master`**. Nunca se commita direto na `master`. Veja
[`docs/desenvolvimento.md`](docs/desenvolvimento.md#fluxo-de-trabalho).

## Idioma

O **português é o idioma oficial** do projeto: documentação, nomes de variáveis,
comentários, mensagens de commit e issues. (Termos técnicos consagrados em inglês
— como *embedding*, *commit*, *deploy* — são mantidos.)

## Licença

[MIT](LICENSE).

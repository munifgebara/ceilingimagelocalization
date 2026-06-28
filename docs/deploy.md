# Deploy no gimli (k3s)

## Ambiente

- Servidor **gimli**: `192.168.0.99` (`ssh munif@192.168.0.99`).
- **k3s** single-node. `kubectl` exige `sudo -n kubectl ...`.
- Ingress **Traefik** (`ingressClassName: traefik`).
- StorageClass padrão: `local-path`.
- **Postgres compartilhado**: `postgres-0` no namespace `platform`, service
  `postgres.platform.svc.cluster.local:5432`, imagem `pgvector/pgvector:pg17`.
  Tem `vector`, `cube`, `earthdistance` (sem PostGIS).
- Exposição externa via **Cloudflare Tunnel** (padrão `cloudflared`).
- **GitHub Actions runner self-hosted** disponível para CI/CD.

## Namespace

Tudo do projeto vai no namespace **`teto`**.

## Banco do projeto

Reusamos o Postgres compartilhado, criando um banco `teto` dedicado:

```sql
CREATE DATABASE teto;
\c teto
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS cube;
CREATE EXTENSION IF NOT EXISTS earthdistance;
```

(As extensões e tabelas também são criadas pelas migrações Alembic.)

## Construir e publicar a imagem

Como o k3s usa containerd (não docker), construímos a imagem com docker no gimli
e importamos no containerd do k3s:

```bash
ssh munif@192.168.0.99 'cd ~/apps/teto/backend && \
  docker build -t teto-api:latest . && \
  docker save teto-api:latest | sudo k3s ctr images import -'
```

## Aplicar os manifestos

```bash
ssh munif@192.168.0.99 'cd ~/apps/teto && sudo -n kubectl apply -k deploy/k8s'
sudo -n kubectl get pods,svc,ingress -n teto
```

Ou use o script: `make deploy-gimli`.

## Exposição via Cloudflare Tunnel

Segue o padrão dos outros apps (deployment `cloudflared` apontando para o service
`teto-api`, com o `TUNNEL_TOKEN` em secret). Ver `deploy/k8s/cloudflared.yaml`.
Configure o hostname desejado no painel da Cloudflare apontando para o service
interno `teto-api.teto.svc.cluster.local:8000`.

## Acesso interno (rede local)

O Ingress responde em `teto.local` (adicione `192.168.0.99 teto.local` ao
`/etc/hosts`), enquanto o túnel não estiver configurado.

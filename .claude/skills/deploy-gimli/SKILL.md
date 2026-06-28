---
name: deploy-gimli
description: Faz o deploy do projeto no servidor gimli (k3s/Kubernetes, namespace teto) e expõe via Cloudflare Tunnel. Use quando pedirem para publicar, fazer deploy, subir no gimli ou atualizar o ambiente em produção.
---

# Deploy no gimli (k3s)

Servidor: `ssh munif@192.168.0.99`. `kubectl` exige `sudo -n`.
Namespace do projeto: **`teto`**. Postgres compartilhado em `platform`.

## Visão geral

Como o k3s é single-node e usa containerd, a imagem é **construída no gimli com
docker e importada no containerd do k3s** (sem registry externo). Os manifestos
ficam em `deploy/k8s/`.

## Passo a passo

1. **Sincronizar o código no gimli** (ou usar o GitHub Actions runner):
   ```bash
   ssh munif@192.168.0.99 'cd ~/apps && \
     (test -d teto && cd teto && git pull) || \
     git clone https://github.com/munifgebara/ceilingimagelocalization.git teto'
   ```

2. **Construir e importar a imagem da API** no k3s:
   ```bash
   ssh munif@192.168.0.99 'cd ~/apps/teto/backend && \
     docker build -t teto-api:latest . && \
     docker save teto-api:latest | sudo k3s ctr images import -'
   ```

3. **Aplicar os manifestos**:
   ```bash
   ssh munif@192.168.0.99 'cd ~/apps/teto && sudo -n kubectl apply -k deploy/k8s'
   ```

4. **Verificar**:
   ```bash
   ssh munif@192.168.0.99 'sudo -n kubectl get pods,svc,ingress -n teto'
   ssh munif@192.168.0.99 'sudo -n kubectl logs -n teto deploy/teto-api --tail=50'
   ```

## Banco de dados

A API usa o Postgres compartilhado (`postgres.platform.svc.cluster.local:5432`).
O banco do projeto é `teto` e as extensões/tabelas são criadas pelas migrações
(`alembic upgrade head`, rodado por um Job/initContainer). Credenciais vêm do
secret `teto-banco` no namespace `teto` (criado a partir do `postgres-secret`).

## Exposição externa (Cloudflare Tunnel)

Segue o padrão dos outros apps no namespace `platform` (deployment `cloudflared`
com secret `TUNNEL_TOKEN`). Ver `deploy/k8s/cloudflared.yaml` e `docs/deploy.md`.

#!/usr/bin/env bash
# Deploy do projeto no gimli (k3s). Roda na maquina local e orquestra via SSH.
# Uso: bash deploy/scripts/deploy-gimli.sh
set -euo pipefail

GIMLI="${GIMLI_USER:-munif}@${GIMLI_HOST:-192.168.0.99}"
REPO="https://github.com/munifgebara/ceilingimagelocalization.git"
DIR="~/apps/teto"
NS="teto"

echo ">> 1/6 Sincronizando o codigo no gimli"
ssh "$GIMLI" "mkdir -p ~/apps && (test -d ~/apps/teto && cd ~/apps/teto && git pull --ff-only || git clone $REPO ~/apps/teto)"

echo ">> 2/6 Garantindo banco 'teto' e extensoes no Postgres compartilhado"
ssh "$GIMLI" 'bash -s' <<"REMOTO"
set -e
PGUSER=postgres
sudo -n kubectl exec -n platform postgres-0 -- sh -c "psql -U $PGUSER -d postgres -tAc \"SELECT 1 FROM pg_database WHERE datname='teto'\" | grep -q 1 || psql -U $PGUSER -d postgres -c 'CREATE DATABASE teto'"
sudo -n kubectl exec -n platform postgres-0 -- sh -c "psql -U $PGUSER -d teto -c 'CREATE EXTENSION IF NOT EXISTS vector; CREATE EXTENSION IF NOT EXISTS cube; CREATE EXTENSION IF NOT EXISTS earthdistance;'"
REMOTO

echo ">> 3/6 Construindo e importando a imagem no k3s"
ssh "$GIMLI" "cd ~/apps/teto/backend && docker build -t teto-api:latest . && docker save teto-api:latest | sudo -n k3s ctr images import -"

echo ">> 4/6 Aplicando namespace + secret + manifestos"
ssh "$GIMLI" 'bash -s' <<"REMOTO"
set -e
sudo -n kubectl apply -f ~/apps/teto/deploy/k8s/namespace.yaml
PGUSER=postgres
PGPASS=$(sudo -n kubectl get secret -n platform postgres-secret -o jsonpath="{.data.postgres-password}" | base64 -d)
URL="postgresql+psycopg://$PGUSER:$PGPASS@postgres.platform.svc.cluster.local:5432/teto"
sudo -n kubectl -n teto create secret generic teto-banco --from-literal=BANCO_URL="$URL" --dry-run=client -o yaml | sudo -n kubectl apply -f -
sudo -n kubectl apply -k ~/apps/teto/deploy/k8s
REMOTO

echo ">> 5/6 Rodando as migracoes (Job)"
ssh "$GIMLI" "sudo -n kubectl -n $NS delete job teto-migracao --ignore-not-found && sudo -n kubectl apply -f ~/apps/teto/deploy/k8s/migracao-job.yaml && sudo -n kubectl -n $NS wait --for=condition=complete job/teto-migracao --timeout=120s"

echo ">> 6/6 Reiniciando a API e verificando"
ssh "$GIMLI" "sudo -n kubectl -n $NS rollout restart deploy/teto-api && sudo -n kubectl -n $NS rollout status deploy/teto-api --timeout=120s && sudo -n kubectl get pods,svc,ingress -n $NS"

echo ">> Deploy concluido."

#!/usr/bin/env bash
# Start the full Compose stack from the repository root.
# Creates JWT keys and deploy/compose/.env when they are missing.
# Does not delete volumes. Exits non-zero when Docker is down or Compose fails.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

COMPOSE=(docker compose -f deploy/compose/docker-compose.yml)
SECRETS=deploy/compose/secrets
ENV_FILE=deploy/compose/.env
PRIV="$SECRETS/jwt_private.pem"
PUB="$SECRETS/jwt_public.pem"

if ! docker info >/dev/null 2>&1; then
  echo "Docker is not running. Start Docker Desktop, then run this script again."
  exit 1
fi

mkdir -p "$SECRETS"
if [[ ! -f "$PRIV" || ! -f "$PUB" ]]; then
  openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048 -out "$PRIV"
  openssl rsa -in "$PRIV" -pubout -out "$PUB"
  echo "Wrote JWT keys under $SECRETS. They are not committed."
else
  echo "JWT keys already exist. They were not replaced."
fi
chmod a+r "$PRIV" "$PUB"

if [[ ! -f "$ENV_FILE" ]]; then
  cp deploy/compose/.env.example "$ENV_FILE"
  echo "Copied deploy/compose/.env.example to $ENV_FILE."
fi

if ! grep -q '^INTERNAL_SERVICE_TOKEN=.\+' "$ENV_FILE"; then
  if grep -q '^INTERNAL_SERVICE_TOKEN=' "$ENV_FILE"; then
    sed -i 's/^INTERNAL_SERVICE_TOKEN=.*/INTERNAL_SERVICE_TOKEN=local-dev/' "$ENV_FILE"
  else
    printf '\nINTERNAL_SERVICE_TOKEN=local-dev\n' >> "$ENV_FILE"
  fi
  echo "Set INTERNAL_SERVICE_TOKEN=local-dev in $ENV_FILE. An empty token makes Odoo fulfillment return 503."
fi

"${COMPOSE[@]}" up -d --build
"${COMPOSE[@]}" ps

cat <<'EOF'

Storefront and API:  http://127.0.0.1:8080
Gateway probe:       http://127.0.0.1:8080/ping
Odoo:                http://127.0.0.1:8069  (admin / admin)
RabbitMQ:            http://127.0.0.1:15672  (order_service / order_service)
Grafana:             http://127.0.0.1:3000
Prometheus:          http://127.0.0.1:9090

Stop without deleting data:
  docker compose -f deploy/compose/docker-compose.yml down

The saga worker is not a Compose service. A live confirm does not reach saga COMPLETED against Odoo.
EOF

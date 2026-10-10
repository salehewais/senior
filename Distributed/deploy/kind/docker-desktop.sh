#!/usr/bin/env bash
# Download every image this stack needs, turn on Docker Desktop Kubernetes,
# load the images into that cluster, and apply namespace commerce.
# After it finishes, open Docker Desktop → Kubernetes → namespace commerce.
# The storefront is http://127.0.0.1:8080
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
export PATH="${HOME}/.local/bin:${PATH}"

PUBLIC_IMAGES=(
  postgres:16-alpine
  rabbitmq:3.13-management-alpine
  redis:7-alpine
  traefik:v3.5.0
  busybox:1.36
  python:3.12-alpine
  otel/opentelemetry-collector:0.114.0
  grafana/tempo:2.6.1
  grafana/grafana:11.3.1
  prom/prometheus:v2.55.1
  prom/alertmanager:v0.27.0
  prometheuscommunity/postgres-exporter:v0.16.0
  oliver006/redis_exporter:v1.66.0
  registry.k8s.io/metrics-server/metrics-server:v0.9.0
)

APP_IMAGES=(
  commerce/order-service:0.1.0
  commerce/reporting-service:0.1.0
  commerce/notification-service:0.1.0
  commerce/frontend:0.1.0
  commerce/jwt-check:0.1.0
  commerce/odoo:18.0.1
)

k8s_state() {
  docker desktop kubernetes status 2>/dev/null \
    | awk -F: '/^State:/ {gsub(/ /,"",$2); print $2; exit}'
}

wait_for_docker() {
  local i
  for i in $(seq 1 60); do
    if docker info >/dev/null 2>&1; then
      return 0
    fi
    echo "Waiting for Docker Desktop (${i}/60)..."
    sleep 5
  done
  echo "Docker Desktop did not start."
  exit 1
}

wait_for_kubernetes() {
  local i state
  for i in $(seq 1 90); do
    state="$(k8s_state || true)"
    echo "Kubernetes status: ${state:-unknown} (${i}/90)"
    if [[ "$state" == "running" ]]; then
      return 0
    fi
    sleep 10
  done
  echo "Kubernetes did not become running. In Docker Desktop open Settings → Kubernetes and enable it."
  exit 1
}

enable_kubernetes() {
  local state
  state="$(k8s_state || true)"
  if [[ "$state" == "running" ]]; then
    echo "Docker Desktop Kubernetes is already running."
    return 0
  fi
  echo "Turning on Docker Desktop Kubernetes."
  docker desktop stop
  python3 - <<'PY'
import json
from pathlib import Path
path = Path.home() / ".docker" / "desktop" / "settings-store.json"
data = json.loads(path.read_text(encoding="utf-8"))
data["KubernetesEnabled"] = True
path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
PY
  docker desktop start
  wait_for_docker
  wait_for_kubernetes
}

prepare_secrets() {
  local secrets="deploy/compose/secrets"
  local env_file="deploy/compose/.env"
  mkdir -p "$secrets"
  if [[ ! -f "$secrets/jwt_private.pem" || ! -f "$secrets/jwt_public.pem" ]]; then
    openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048 -out "$secrets/jwt_private.pem"
    openssl rsa -in "$secrets/jwt_private.pem" -pubout -out "$secrets/jwt_public.pem"
    echo "Wrote JWT keys under $secrets."
  else
    echo "JWT keys already exist."
  fi
  chmod a+r "$secrets/jwt_private.pem" "$secrets/jwt_public.pem"
  if [[ ! -f "$env_file" ]]; then
    cp deploy/compose/.env.example "$env_file"
  fi
  if ! grep -q '^INTERNAL_SERVICE_TOKEN=.\+' "$env_file"; then
    if grep -q '^INTERNAL_SERVICE_TOKEN=' "$env_file"; then
      sed -i 's/^INTERNAL_SERVICE_TOKEN=.*/INTERNAL_SERVICE_TOKEN=local-dev/' "$env_file"
    else
      printf '\nINTERNAL_SERVICE_TOKEN=local-dev\n' >> "$env_file"
    fi
    echo "Set INTERNAL_SERVICE_TOKEN=local-dev in $env_file."
  fi
}

load_image() {
  local image="$1"
  local node
  mapfile -t nodes < <(docker ps --format '{{.Names}}' | awk '/^desktop-/')
  if [[ ${#nodes[@]} -eq 0 ]]; then
    echo "No Kubernetes nodes are running, so ${image} was not loaded into the cluster."
    exit 1
  fi
  for node in "${nodes[@]}"; do
    echo "Loading ${image} into ${node}"
    docker save "$image" | docker exec -i "$node" ctr --namespace k8s.io images import -
  done
}

apply_file() {
  local name="$1"
  shift
  kubectl -n commerce create configmap "$name" "$@" --dry-run=client -o yaml | kubectl apply -f -
}

if ! command -v docker >/dev/null 2>&1; then
  echo "The docker command is not installed."
  exit 1
fi
if ! command -v kubectl >/dev/null 2>&1; then
  echo "kubectl is not installed. Expected it on PATH or in ${HOME}/.local/bin."
  exit 1
fi

if ! docker info >/dev/null 2>&1; then
  echo "Starting Docker Desktop."
  docker desktop start
  wait_for_docker
fi

enable_kubernetes
kubectl config use-context docker-desktop
kubectl wait --for=condition=Ready nodes --all --timeout=180s

echo "Downloading public images."
for image in "${PUBLIC_IMAGES[@]}"; do
  docker pull "$image"
done

echo "Building application images."
docker build -t commerce/order-service:0.1.0 services/order-service
docker build -t commerce/reporting-service:0.1.0 services/reporting-service
docker build -t commerce/notification-service:0.1.0 services/notification-service
docker build -t commerce/frontend:0.1.0 \
  --build-arg VITE_API_BASE_URL=http://127.0.0.1:8080 \
  services/frontend
docker build -t commerce/jwt-check:0.1.0 \
  -f deploy/gateway/jwt-check/Dockerfile \
  deploy/gateway
docker build -t commerce/odoo:18.0.1 services/odoo

echo "Loading images into the Docker Desktop Kubernetes nodes."
for image in "${PUBLIC_IMAGES[@]}" "${APP_IMAGES[@]}"; do
  load_image "$image"
done

prepare_secrets
kubectl apply -f deploy/kind/namespace.yaml

apply_file gateway-config \
  --from-file=traefik.yaml=deploy/kind/traefik-gateway.yaml \
  --from-file=dynamic.yaml=deploy/compose/dynamic.yaml
apply_file gateway-plugin \
  --from-file=edgeheaders.go=deploy/gateway/plugins-local/src/github.com/commerce/edgeheaders/edgeheaders.go \
  --from-file=go.mod=deploy/gateway/plugins-local/src/github.com/commerce/edgeheaders/go.mod \
  --from-file=traefik.yml=deploy/gateway/plugins-local/src/github.com/commerce/edgeheaders/.traefik.yml
apply_file ingress-config \
  --from-file=traefik.yaml=deploy/kind/traefik-ingress.yaml
apply_file prometheus-config \
  --from-file=prometheus.yml=deploy/observability/prometheus/prometheus.yml \
  --from-file=alerts.yml=deploy/observability/prometheus/alerts.yml
apply_file alertmanager-config \
  --from-file=alertmanager.yml=deploy/observability/alertmanager/alertmanager.yml
apply_file otel-config \
  --from-file=collector.yaml=deploy/observability/otel/collector.yaml
apply_file tempo-config \
  --from-file=tempo.yaml=deploy/observability/tempo/tempo.yaml
apply_file grafana-datasources \
  --from-file=datasources.yml=deploy/observability/grafana/provisioning/datasources/datasources.yml
apply_file grafana-dashboard-provider \
  --from-file=dashboards.yml=deploy/observability/grafana/provisioning/dashboards/dashboards.yml
apply_file grafana-dashboards \
  --from-file=deploy/observability/grafana/dashboards
apply_file rabbitmq-plugins \
  --from-file=enabled_plugins=deploy/observability/rabbitmq/enabled_plugins
apply_file odoo-config \
  --from-file=odoo.conf=services/odoo/config/odoo.conf
apply_file alert-webhook-script \
  --from-file=hook.py=deploy/observability/webhook/hook.py

bash deploy/kind/create-secrets.sh
kubectl apply -k deploy/kind
kubectl -n commerce rollout status deploy/ingress --timeout=180s || true

cat <<'EOF'

Docker Desktop Kubernetes is running namespace commerce.
Open Docker Desktop, choose Kubernetes, and select the commerce namespace.
The pods are already started. There is no separate Run button for each image.

Storefront: http://127.0.0.1:8080
EOF

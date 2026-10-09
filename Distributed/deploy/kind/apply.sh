#!/usr/bin/env bash
# Build the Compose image tags, load them into kind, and apply deploy/kind.
# Does not delete a cluster. Compose remains the first runtime.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
CLUSTER="${KIND_CLUSTER_NAME:-commerce}"

if ! docker info >/dev/null 2>&1; then
  echo "Docker is not running. Manifests are in deploy/kind. The cluster was not created."
  exit 1
fi
if ! command -v kind >/dev/null 2>&1 || ! command -v kubectl >/dev/null 2>&1; then
  echo "kind and kubectl are required. The cluster was not created."
  exit 1
fi

if kind get clusters 2>/dev/null | grep -qx "$CLUSTER"; then
  echo "kind cluster ${CLUSTER} already exists. It will not be deleted."
else
  kind create cluster --config deploy/kind/kind-config.yaml
fi

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

for image in \
  commerce/order-service:0.1.0 \
  commerce/reporting-service:0.1.0 \
  commerce/notification-service:0.1.0 \
  commerce/frontend:0.1.0 \
  commerce/jwt-check:0.1.0 \
  commerce/odoo:18.0.1
do
  kind load docker-image --name "$CLUSTER" "$image"
done

kubectl apply -f deploy/kind/namespace.yaml

apply_file() {
  local name="$1"
  shift
  kubectl -n commerce create configmap "$name" "$@" --dry-run=client -o yaml | kubectl apply -f -
}

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

echo "Applied namespace commerce. Public HTTP is http://127.0.0.1:8080 through the Ingress to the gateway."
echo "order-service starts at 2 replicas. The HPA watches CPU once metrics-server is Ready."
echo "This kind cluster is one node, HTTP, and local images. It is not production."

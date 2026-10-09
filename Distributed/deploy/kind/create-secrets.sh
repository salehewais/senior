#!/usr/bin/env bash
# Create Secret commerce-secrets from host PEM files and INTERNAL_SERVICE_TOKEN.
# Does not write the key or the token into the git tree.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
NS="${NAMESPACE:-commerce}"
PRIV="${JWT_PRIVATE_KEY_PATH:-$ROOT/deploy/compose/secrets/jwt_private.pem}"
PUB="${JWT_PUBLIC_KEY_PATH:-$ROOT/deploy/compose/secrets/jwt_public.pem}"

if [[ ! -f "$PRIV" || ! -f "$PUB" ]]; then
  echo "Missing JWT PEM files."
  echo "Generate them on the host, then re-run. They stay out of git."
  echo "  mkdir -p deploy/compose/secrets"
  echo "  openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048 -out deploy/compose/secrets/jwt_private.pem"
  echo "  openssl rsa -in deploy/compose/secrets/jwt_private.pem -pubout -out deploy/compose/secrets/jwt_public.pem"
  echo "Expected: $PRIV"
  echo "Expected: $PUB"
  exit 1
fi

if [[ -z "${INTERNAL_SERVICE_TOKEN+x}" && -f "$ROOT/deploy/compose/.env" ]]; then
  INTERNAL_SERVICE_TOKEN="$(
    python3 - "$ROOT/deploy/compose/.env" <<'PY'
import sys
from pathlib import Path

for line in Path(sys.argv[1]).read_text(encoding="utf-8").splitlines():
    stripped = line.strip()
    if not stripped or stripped.startswith("#") or "=" not in stripped:
        continue
    key, value = stripped.split("=", 1)
    if key.strip() == "INTERNAL_SERVICE_TOKEN":
        print(value.strip().strip('"').strip("'"), end="")
        break
PY
  )"
fi
TOKEN="${INTERNAL_SERVICE_TOKEN-}"

kubectl apply -f "$ROOT/deploy/kind/namespace.yaml"
kubectl -n "$NS" create secret generic commerce-secrets \
  --from-file=jwt_private.pem="$PRIV" \
  --from-file=jwt_public.pem="$PUB" \
  --from-literal=INTERNAL_SERVICE_TOKEN="$TOKEN" \
  --dry-run=client -o yaml | kubectl apply -f -

echo "Applied Secret commerce-secrets in namespace ${NS}. PEM files were not written to git."

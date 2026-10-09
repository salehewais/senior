#!/usr/bin/env bash
# Stop Redis. Catalog reads still use order_db. Login and order create fail closed. Start Redis and those routes work again.
set -euo pipefail

LAB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib.sh
source "${LAB_DIR}/lib.sh"

SERVICE=redis
action="$(lab_action "${1:-}")"
require_docker

case "${action}" in
  stop)
    printf '%s\n' "About to stop only the Compose service redis (deploy/compose)."
    printf '%s\n' "Log in first, while Redis is up, and keep the access token. order-service and postgres stay up."
    compose stop "${SERVICE}"
    cat <<'EOF'
Stopped redis. The product cache treats a dead Redis as a miss. Login and order create fail closed.

Look at:
- GET http://127.0.0.1:8080/api/v1/products with the access token you already have.
  The gateway still checks that token. jwt-check does not use Redis.
  Expect HTTP 200 when order_db is up. The list is the Postgres catalog, not a cache hit.
  The process logs "product cache read skipped; using the database" at debug. The default level is INFO, so do not wait for that line. The 200 is the observation.
- POST http://127.0.0.1:8080/api/v1/auth/login
  Expect HTTP 503 and error.code DEPENDENCY_UNAVAILABLE. The message is "The rate limit service is unavailable."
  The password checker does not run. No new session is created.
- POST http://127.0.0.1:8080/api/v1/orders with the same access token.
  Expect HTTP 503 and error.code DEPENDENCY_UNAVAILABLE, before an order row is written.
- POST http://127.0.0.1:8080/api/v1/auth/register fails the same way. An access token that is still valid keeps working for routes that do not need Redis.
  Confirm, order read, refresh, and logout do not use Redis.

Orders were never stored in Redis. A stopped Redis does not remove an order.
EOF
    ;;
  start)
    printf '%s\n' "About to start only the Compose service redis (deploy/compose)."
    compose start "${SERVICE}"
    cat <<'EOF'
Started redis. Login and order create should succeed again. The catalog cache fills on the next miss. Limits apply again.

Look at:
- POST http://127.0.0.1:8080/api/v1/auth/login returns a token (HTTP 200), unless the existing limit answers first.
- POST http://127.0.0.1:8080/api/v1/orders returns HTTP 201 when the body is valid and the limit is not exhausted.
- GET http://127.0.0.1:8080/api/v1/products still returns HTTP 200.
- A 429 with error.code RATE_LIMITED means the limiter is back. Login allows 5 per minute. Order create allows 10 per minute. This lab does not change those limits.
EOF
    ;;
esac

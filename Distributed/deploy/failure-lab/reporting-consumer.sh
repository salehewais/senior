#!/usr/bin/env bash
# Stop the reporting consumer. Confirm still succeeds. Start it and the projection catches up.
set -euo pipefail

LAB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib.sh
source "${LAB_DIR}/lib.sh"

SERVICE=reporting-consumer
action="$(lab_action "${1:-}")"
require_docker

case "${action}" in
  stop)
    printf '%s\n' "About to stop only the Compose service reporting-consumer (deploy/compose)."
    printf '%s\n' "order-service, order-outbox-publisher, reporting-service, and rabbitmq stay up."
    compose stop "${SERVICE}"
    cat <<'EOF'
Stopped reporting-consumer. Confirm an order through the public API. The HTTP call does not wait on this consumer.

Look at:
- POST http://127.0.0.1:8080/api/v1/orders/{order_id}/confirm
  Use an access token you already have. Expect HTTP 200 and order status CONFIRMED.
  Create a PENDING order first with POST http://127.0.0.1:8080/api/v1/orders if you need one.
  Send product_id and quantity only. The server prices the line.
- Queue q.reporting.projection. From deploy/compose:
    docker compose -f docker-compose.yml exec rabbitmq rabbitmqctl list_queues name messages
  The management UI is http://127.0.0.1:15672 (the learning user is in "How to run the full stack").
  Depth grows because the publisher still sends and nothing is acking this queue.
- reporting-service can still answer from the rows already in reporting_db. New facts are not in that projection yet.
- This script does not stop odoo-consumer. q.odoo.order-confirmed is a different queue.

Do not point Django at order_db to catch up.
EOF
    ;;
  start)
    printf '%s\n' "About to start only the Compose service reporting-consumer (deploy/compose)."
    compose start "${SERVICE}"
    cat <<'EOF'
Started reporting-consumer. It should drain q.reporting.projection. The same event_id is applied once.

Look at:
- Queue q.reporting.projection. messages falls as the consumer acks.
- Logs: docker compose -f docker-compose.yml logs -f reporting-consumer
  A redelivery logs: delivery acked event_id=... event_type=... correlation_id=... reason=duplicate
  reason=duplicate means the projection was not changed again. The consumer does not use requeue=true.
- From deploy/compose, in reporting_db:
    docker compose -f docker-compose.yml exec reporting-postgres \
      psql -U reporting_service -d reporting_db -c \
      "SELECT order_id, status, aggregate_version, total_amount_minor FROM order_projections WHERE order_id = '<order_id>';"
    docker compose -f docker-compose.yml exec reporting-postgres \
      psql -U reporting_service -d reporting_db -c \
      "SELECT event_id, event_type FROM processed_events WHERE aggregate_id = '<order_id>';"
  One projection row. total_amount_minor is the order total once. event_id is the primary key, so a second insert of that id does not commit.
EOF
    ;;
esac

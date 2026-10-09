#!/usr/bin/env bash
# Stop RabbitMQ. The order HTTP call still commits. The outbox row stays pending. Start the broker and the publisher drains it.
set -euo pipefail

LAB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib.sh
source "${LAB_DIR}/lib.sh"

SERVICE=rabbitmq
action="$(lab_action "${1:-}")"
require_docker

case "${action}" in
  stop)
    printf '%s\n' "About to stop only the Compose service rabbitmq (deploy/compose)."
    printf '%s\n' "order-service and order-outbox-publisher stay up. The API does not call the broker."
    compose stop "${SERVICE}"
    cat <<'EOF'
Stopped rabbitmq. Create an order or confirm one. The HTTP call still commits in order_db. The outbox row stays pending.

Look at:
- POST http://127.0.0.1:8080/api/v1/orders or POST http://127.0.0.1:8080/api/v1/orders/{order_id}/confirm
  Expect the same success you get when the broker is up (201 on create, 200 and status CONFIRMED on confirm).
- Publisher logs, from deploy/compose:
    docker compose -f docker-compose.yml logs -f order-outbox-publisher
  A failed confirm logs: outbox publish failed; row stays pending event_id=... event_type=... correlation_id=... retry_count=...
  The line does not include the payload.
- Pending rows, from deploy/compose:
    docker compose -f docker-compose.yml exec postgres \
      psql -U order_service -d order_db -c \
      "SELECT id, event_type, status, retry_count, published_at FROM outbox WHERE status IN ('pending', 'failed') ORDER BY created_at, id;"
  status stays pending. published_at stays empty. Queues do not grow while the broker is stopped.
  http://127.0.0.1:15672 does not answer until rabbitmq is started again.

OUTBOX_MAX_ATTEMPTS is 5. The poll interval is 1 second. If the broker stays down through five failed confirms, the row becomes status=failed and the publisher stops claiming it. The log line is: outbox row failed; the business row is unchanged. That is not a consumer dead-letter queue. Do not delete the outbox row.
EOF
    ;;
  start)
    printf '%s\n' "About to start only the Compose service rabbitmq (deploy/compose)."
    compose start "${SERVICE}"
    cat <<'EOF'
Started rabbitmq. Leave order-outbox-publisher running. It publishes rows that are still pending. It does not invent a message for a row that is already published.

Look at:
- The same SELECT on outbox. A row that was pending moves to status=published and published_at is set. retry_count stays where it was.
- After the management UI answers, queue depth can rise and then fall as consumers ack. From deploy/compose:
    docker compose -f docker-compose.yml exec rabbitmq rabbitmqctl list_queues name messages
- If a row is already status=failed, the publisher will not claim it. Set that row back to pending and set retry_count to 0, and record why. Do not delete the row.
    docker compose -f docker-compose.yml exec postgres \
      psql -U order_service -d order_db -c \
      "UPDATE outbox SET status = 'pending', retry_count = 0 WHERE id = '<event_id>' AND status = 'failed';"
  Run that only for a failed row, after the broker is back. A pending row does not need it.
EOF
    ;;
esac

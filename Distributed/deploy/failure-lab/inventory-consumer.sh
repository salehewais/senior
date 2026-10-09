#!/usr/bin/env bash
# Stop the inventory consumer. Confirm still succeeds. q.order.inventory grows for InventoryUpdated. A duplicate event_id does not apply twice.
set -euo pipefail

LAB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib.sh
source "${LAB_DIR}/lib.sh"

SERVICE=order-inventory-consumer
action="$(lab_action "${1:-}")"
require_docker

case "${action}" in
  stop)
    printf '%s\n' "About to stop only the Compose service order-inventory-consumer (deploy/compose)."
    printf '%s\n' "order-service, order-outbox-publisher, and rabbitmq stay up."
    compose stop "${SERVICE}"
    cat <<'EOF'
Stopped order-inventory-consumer. The publish path for an order confirm still commits and the publisher can still send.

Look at:
- POST http://127.0.0.1:8080/api/v1/orders/{order_id}/confirm
  Expect HTTP 200 and status CONFIRMED. That fact is OrderConfirmed. It is not routed to q.order.inventory.
- Queue q.order.inventory. It is bound to inventory.updated on erp.events.
  Depth grows when odoo-publisher sends InventoryUpdated while this consumer is stopped.
  A stock change in the Odoo UI (http://127.0.0.1:8069, learning login in "How to run the full stack") is what produces that message.
  This script does not stop odoo or odoo-publisher.
  From deploy/compose:
    docker compose -f docker-compose.yml exec rabbitmq rabbitmqctl list_queues name messages
  Watch the messages column for q.order.inventory. The management UI is http://127.0.0.1:15672.
- If nothing publishes InventoryUpdated during the stop, the depth stays where it was. Confirm can still succeed.
EOF
    ;;
  start)
    printf '%s\n' "About to start only the Compose service order-inventory-consumer (deploy/compose)."
    compose start "${SERVICE}"
    cat <<'EOF'
Started order-inventory-consumer. It should drain q.order.inventory. One event_id updates the snapshot once.

Look at:
- Queue q.order.inventory. messages falls as deliveries are acked.
- Logs: docker compose -f docker-compose.yml logs -f order-inventory-consumer
  A second delivery of the same event_id logs: duplicate delivery acked without a second effect event_id=... event_type=...
  The consumer does not use requeue=true. A duplicate is acked. The snapshot is not applied again.
- From deploy/compose, in order_db:
    docker compose -f docker-compose.yml exec postgres \
      psql -U order_service -d order_db -c \
      "SELECT event_id, event_type, consumer_name FROM processed_events WHERE consumer_name = 'order-inventory' ORDER BY processed_at DESC LIMIT 20;"
    docker compose -f docker-compose.yml exec postgres \
      psql -U order_service -d order_db -c \
      "SELECT product_id, quantity_on_hand, quantity_reserved, source_version FROM inventory_snapshots WHERE product_id = '<product_id>';"
  event_id is the primary key. One row per delivery that committed. quantity_on_hand moves once for that event_id.
  The unit test that already locks this in is test_duplicate_event_id_does_not_apply_twice.
EOF
    ;;
esac

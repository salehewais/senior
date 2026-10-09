#!/usr/bin/env bash
# Dump one Compose Postgres database in custom format.
# Redis is a cache and is not dumped. RabbitMQ is not dumped.
# The other two databases are not dumped.
set -euo pipefail

BACKUP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib.sh
source "${BACKUP_DIR}/lib.sh"

if [ "$#" -ne 1 ]; then
  printf '%s\n' "Usage: $0 <order_db|reporting_db|odoo_db>" >&2
  exit 2
fi

db="$1"
service="$(resolve_database "${db}")"
require_docker
assert_container_database "${service}" "${db}"

mkdir -p "${DUMPS_DIR}"
outfile="${DUMPS_DIR}/${db}-$(date -u +%Y%m%dT%H%M%SZ).dump"
partial="${DUMPS_DIR}/.${db}.partial.dump"
rm -f "${partial}"

printf '%s\n' "Dumping only ${db} from Compose service ${service}. Redis, RabbitMQ, and the other databases are not included."

# POSTGRES_PASSWORD is already in the container. This script does not set a new password.
if ! (
  cd "${COMPOSE_DIR}"
  docker compose -f docker-compose.yml exec -T "${service}" \
    sh -c 'export PGPASSWORD="$POSTGRES_PASSWORD"; pg_dump --no-password --host /var/run/postgresql --format=custom --no-owner --no-acl --username "$POSTGRES_USER" --dbname "$POSTGRES_DB"'
) > "${partial}"; then
  rm -f "${partial}"
  printf '%s\n' "Dump of ${db} failed. No dump was kept." >&2
  exit 1
fi

if ! dump_db="$(archive_dbname "${service}" "${partial}")"; then
  rm -f "${partial}"
  exit 1
fi
if ! refuse_cross_database "${dump_db}" "${db}" "keep"; then
  rm -f "${partial}"
  exit 1
fi

mv "${partial}" "${outfile}"
printf '%s\n' "Wrote ${outfile}"

#!/usr/bin/env bash
# Replace objects inside one Compose Postgres database from a custom-format dump.
# Requires --yes. Prints the database name it is about to replace.
# Does not drop the other two databases. Does not drop RabbitMQ or Redis data.
# Redis is a cache and is not restored. A restore is not a rewind of the broker.
set -euo pipefail

BACKUP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib.sh
source "${BACKUP_DIR}/lib.sh"

if [ "$#" -eq 0 ]; then
  printf '%s\n' "Usage: $0 <order_db|reporting_db|odoo_db> <dump-file> --yes" >&2
  exit 2
fi

db=""
dump=""
confirmed=0
for arg in "$@"; do
  case "${arg}" in
    --yes) confirmed=1 ;;
    --*)
      printf '%s\n' "Refusing unknown option '${arg}'. Restore requires --yes." >&2
      exit 2
      ;;
    *)
      if [ -z "${db}" ]; then
        db="${arg}"
      elif [ -z "${dump}" ]; then
        dump="${arg}"
      else
        printf '%s\n' "Refusing extra argument '${arg}'." >&2
        exit 2
      fi
      ;;
  esac
done

if [ "${confirmed}" -ne 1 ]; then
  printf '%s\n' "Refusing to replace data in ${db:-a database} without --yes." >&2
  exit 2
fi

if [ -z "${db}" ] || [ -z "${dump}" ]; then
  printf '%s\n' "Usage: $0 <order_db|reporting_db|odoo_db> <dump-file> --yes" >&2
  exit 2
fi

service="$(resolve_database "${db}")"

if [ ! -f "${dump}" ]; then
  printf '%s\n' "Refusing: dump file '${dump}' does not exist. Nothing was restored." >&2
  exit 2
fi

require_docker
assert_container_database "${service}" "${db}"

if ! dump_db="$(archive_dbname "${service}" "${dump}")"; then
  exit 1
fi
if ! refuse_cross_database "${dump_db}" "${db}" "restore"; then
  exit 1
fi

printf '%s\n' "About to replace the data in ${db} on Compose service ${service}. The other two databases stay. RabbitMQ and Redis are not changed."

started_at="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
start_epoch="$(date -u +%s)"
printf '%s\n' "Restore start ${started_at}."
mkdir -p "${DUMPS_DIR}"
printf '%s\n' "database=${db}" "start=${started_at}" > "${DUMPS_DIR}/last-restore.txt"

# pg_restore --clean replaces objects inside this database. It does not create or drop a database.
# POSTGRES_PASSWORD is already in the container. This script does not set a new password.
if ! (
  cd "${COMPOSE_DIR}"
  docker compose -f docker-compose.yml exec -T "${service}" \
    sh -c 'export PGPASSWORD="$POSTGRES_PASSWORD"; pg_restore --no-password --host /var/run/postgresql --clean --if-exists --no-owner --no-acl --single-transaction --exit-on-error --dbname "$POSTGRES_DB"'
) < "${dump}"; then
  printf '%s\n' "Restore of ${db} failed. The other databases were not the target of this command." >&2
  exit 1
fi

finished_at="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
end_epoch="$(date -u +%s)"
elapsed="$((end_epoch - start_epoch))"
printf '%s\n' "Restore end ${finished_at}."
printf '%s\n' "Elapsed seconds for this restore of ${db}: ${elapsed}."
{
  printf '%s\n' "database=${db}"
  printf '%s\n' "start=${started_at}"
  printf '%s\n' "end=${finished_at}"
  printf '%s\n' "elapsed_seconds=${elapsed}"
} > "${DUMPS_DIR}/last-restore.txt"

# Shared helpers for Phase 19 backup and restore.
# Dump and restore scripts source this file. It is not a backup by itself.
# A failing `docker info` returns before any dump or restore.
# Redis is a cache and is not backed up. RabbitMQ is not backed up.
# The database name comes from the caller and from the dump archive header.
# The file name is not the database name.

: "${BACKUP_DIR:?BACKUP_DIR is not set}"

COMPOSE_DIR="$(cd "${BACKUP_DIR}/../compose" && pwd)"
COMPOSE_FILE="${COMPOSE_DIR}/docker-compose.yml"
DUMPS_DIR="${BACKUP_DIR}/dumps"

require_docker() {
  if ! docker info >/dev/null 2>&1; then
    printf '%s\n' "Docker is not available: docker info failed. Nothing was dumped or restored." >&2
    exit 1
  fi
}

# order_db, reporting_db, and odoo_db are three Postgres servers in deploy/compose.
# Any other name is refused. The value printed is the Compose service, not a host port.
resolve_database() {
  case "${1:-}" in
    order_db) printf '%s\n' "postgres" ;;
    reporting_db) printf '%s\n' "reporting-postgres" ;;
    odoo_db) printf '%s\n' "odoo-db" ;;
    *)
      printf '%s\n' "Refusing database '${1:-}'. Only order_db, reporting_db, and odoo_db can be dumped or restored, each on its own Compose Postgres service." >&2
      exit 2
      ;;
  esac
}

assert_container_database() {
  local service="$1"
  local db="$2"
  local actual
  if ! actual="$(
    cd "${COMPOSE_DIR}"
    docker compose -f docker-compose.yml exec -T "${service}" printenv POSTGRES_DB
  )"; then
    printf '%s\n' "Could not read POSTGRES_DB from ${service}. Nothing was dumped or restored." >&2
    return 1
  fi
  actual="${actual//$'\r'/}"
  if [ "${actual}" != "${db}" ]; then
    printf '%s\n' "Refusing: Compose service ${service} has POSTGRES_DB '${actual}', not ${db}. A backup of one database is not taken from another." >&2
    return 1
  fi
}

# dbname comes from `pg_restore --list` (the archive header), not from the file name.
archive_dbname() {
  local service="$1"
  local dump_path="$2"
  local listing
  local dump_db
  if [ "${dump_path#/}" = "${dump_path}" ]; then
    dump_path="$(pwd)/${dump_path}"
  fi
  if ! listing="$(
    cd "${COMPOSE_DIR}"
    docker compose -f docker-compose.yml exec -T "${service}" pg_restore --list < "${dump_path}"
  )"; then
    printf '%s\n' "Refusing: could not read the dump archive header. Nothing further was dumped or restored." >&2
    return 1
  fi
  dump_db="$(printf '%s\n' "${listing}" | sed -n 's/^;[[:space:]]*dbname:[[:space:]]*//p')"
  dump_db="${dump_db%%$'\n'*}"
  dump_db="${dump_db//$'\r'/}"
  if [ -z "${dump_db}" ]; then
    printf '%s\n' "Refusing: the dump does not name a database in its archive header. The file name is not used as the database name." >&2
    return 1
  fi
  printf '%s\n' "${dump_db}"
}

# Header dbname must be one of the three databases and must equal the target.
# action is "restore" or "keep" and is only used in the message.
refuse_cross_database() {
  local dump_db="$1"
  local db="$2"
  local action="$3"
  case "${dump_db}" in
    order_db|reporting_db|odoo_db) ;;
    *)
      printf '%s\n' "Refusing to ${action}: the archive header names '${dump_db}', which is not order_db, reporting_db, or odoo_db." >&2
      return 1
      ;;
  esac
  if [ "${dump_db}" != "${db}" ]; then
    printf '%s\n' "Refusing to ${action} a dump of ${dump_db} into ${db}. A dump of one database is not applied to another." >&2
    return 1
  fi
  return 0
}

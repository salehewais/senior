# Shared helpers for the Phase 18 failure lab.
# Experiment scripts source this file. It is not a drill by itself.
# A failing `docker info` returns before any Compose stop or start.

: "${LAB_DIR:?LAB_DIR is not set}"

COMPOSE_DIR="$(cd "${LAB_DIR}/../compose" && pwd)"
COMPOSE_FILE="${COMPOSE_DIR}/docker-compose.yml"

require_docker() {
  if ! docker info >/dev/null 2>&1; then
    printf '%s\n' "Docker is not available: docker info failed. Nothing was stopped or started." >&2
    exit 1
  fi
}

# Only `stop` or `start`, and only the service this script named in SERVICE.
compose() {
  if [ "$#" -ne 2 ]; then
    printf '%s\n' "Refusing a compose command that does not name exactly one service." >&2
    exit 1
  fi
  case "$1" in
    stop|start) ;;
    *)
      printf '%s\n' "Refusing compose command '$1'. This lab only stops or starts one service." >&2
      exit 1
      ;;
  esac
  if [ "$2" != "${SERVICE}" ]; then
    printf '%s\n' "Refusing to ${1} '$2'. This script only changes ${SERVICE}." >&2
    exit 1
  fi
  (
    cd "${COMPOSE_DIR}"
    docker compose -f docker-compose.yml "$1" "$2"
  )
}

lab_action() {
  case "${1:-}" in
    stop|start) printf '%s\n' "$1" ;;
    *)
      printf '%s\n' "Usage: $0 stop|start" >&2
      printf '%s\n' "Only the Compose service ${SERVICE} in deploy/compose is stopped or started." >&2
      exit 2
      ;;
  esac
}

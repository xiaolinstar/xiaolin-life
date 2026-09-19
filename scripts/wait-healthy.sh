#!/usr/bin/env bash
# Wait for the xiaolin-life container to become healthy.
# Exits 0 on success; on failure prints docker inspect + logs and exits 1.
#
# Used by .github/workflows/cd-ghcr.yml after `docker compose up -d`.
# Designed to fail loudly so misconfigured deployments are detected
# at deploy time, not silently via GH Actions success.
#
# Usage:
#   scripts/wait-healthy.sh [--timeout=SECONDS] [--name=CONTAINER]

set -euo pipefail

CONTAINER_NAME="xiaolin-life-website"
TIMEOUT_SECS=120
STAGE1_SECS=40

usage() {
  cat <<EOF
Usage: $0 [OPTIONS]

Options:
  --name=NAME         Container name (default: $CONTAINER_NAME)
  --timeout=SECS      Total timeout in seconds (default: $TIMEOUT_SECS)
  --stage1=SECS       Stage 1 timeout (default: $STAGE1_SECS)
  -h, --help          Show this help

Exit codes:
  0   Container healthy
  1   Container failed to start or did not become healthy
  2   Invalid arguments / missing tools
  130 Interrupted (SIGINT/SIGTERM)
EOF
}

for arg in "$@"; do
  case "$arg" in
    --name=*)     CONTAINER_NAME="${arg#*=}" ;;
    --timeout=*)  TIMEOUT_SECS="${arg#*=}" ;;
    --stage1=*)   STAGE1_SECS="${arg#*=}" ;;
    -h|--help)    usage; exit 0 ;;
    *)            echo "Unknown argument: $arg" >&2; usage >&2; exit 2 ;;
  esac
done

command -v docker >/dev/null 2>&1 || { echo "ERROR: docker not in PATH" >&2; exit 2; }

if (( STAGE1_SECS >= TIMEOUT_SECS )); then
  echo "ERROR: --stage1 ($STAGE1_SECS) must be < --timeout ($TIMEOUT_SECS)" >&2
  exit 2
fi

# Detect compose file relative to current directory
COMPOSE_FILE="compose.yaml"
if [[ ! -f "$COMPOSE_FILE" && -f "../$COMPOSE_FILE" ]]; then
  COMPOSE_FILE="../$COMPOSE_FILE"
fi

log()  { printf '[%s] %s\n' "$(date '+%H:%M:%S')" "$*"; }
now()  { date +%s; }

cleanup() {
  echo
  log "Interrupted — final container state:"
  docker inspect --format='{{json .State}}' "$CONTAINER_NAME" 2>/dev/null || true
  exit 130
}
trap cleanup INT TERM

STAGE2_SECS=$(( TIMEOUT_SECS - STAGE1_SECS ))

# Stage 1: container status=running
log "Stage 1/2: wait '$CONTAINER_NAME' status=running (timeout ${STAGE1_SECS}s)"
DEADLINE=$(( $(now) + STAGE1_SECS ))
STATUS="missing"
attempt=0
while (( $(now) < DEADLINE )); do
  attempt=$(( attempt + 1 ))
  STATUS=$(docker inspect --format='{{.State.Status}}' "$CONTAINER_NAME" 2>/dev/null || echo "missing")
  log "  attempt $attempt: status=$STATUS"
  if [[ "$STATUS" == "running" ]]; then
    break
  fi
  sleep 5
done

if [[ "$STATUS" != "running" ]]; then
  log "FAILED: container did not reach 'running' in ${STAGE1_SECS}s"
  log "--- docker compose ps ---"
  docker compose -f "$COMPOSE_FILE" ps 2>&1 || true
  log "--- docker logs (tail 80) ---"
  docker logs --tail=80 "$CONTAINER_NAME" 2>&1 || true
  exit 1
fi

# Stage 2: healthcheck=healthy
log "Stage 2/2: wait '$CONTAINER_NAME' health=healthy (timeout ${STAGE2_SECS}s)"
DEADLINE=$(( $(now) + STAGE2_SECS ))
HEALTH="missing"
attempt=0
while (( $(now) < DEADLINE )); do
  attempt=$(( attempt + 1 ))
  HEALTH=$(docker inspect --format='{{.State.Health.Status}}' "$CONTAINER_NAME" 2>/dev/null || echo "missing")
  log "  attempt $attempt: health=$HEALTH"
  case "$HEALTH" in
    healthy)
      log "OK: container healthy after ${attempt} attempts"
      exit 0
      ;;
    unhealthy)
      log "FAILED: healthcheck reports unhealthy"
      log "--- docker inspect health ---"
      docker inspect --format='{{json .State.Health}}' "$CONTAINER_NAME" 2>&1 || true
      log "--- docker logs (tail 80) ---"
      docker logs --tail=80 "$CONTAINER_NAME" 2>&1 || true
      exit 1
      ;;
  esac
  sleep 5
done

log "FAILED: did not become healthy in ${TIMEOUT_SECS}s total"
log "--- docker inspect health ---"
docker inspect --format='{{json .State.Health}}' "$CONTAINER_NAME" 2>&1 || true
log "--- docker logs (tail 80) ---"
docker logs --tail=80 "$CONTAINER_NAME" 2>&1 || true
exit 1
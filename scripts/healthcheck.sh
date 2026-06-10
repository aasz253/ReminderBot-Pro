#!/usr/bin/env bash
set -euo pipefail

# ─── ReminderBot Pro - Health Check Script ────────────────────────────────────

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
GRAY='\033[0;90m'
NC='\033[0m'

PASS="${GREEN}✓${NC}"
FAIL="${RED}✗${NC}"
SKIP="${YELLOW}~${NC}"

EXIT_CODE=0

check() {
  local name="$1"
  local status="$2"
  local detail="${3:-}"

  if [[ "$status" == "pass" ]]; then
    echo -e "  ${PASS} ${name} ${GRAY}${detail}${NC}"
  elif [[ "$status" == "fail" ]]; then
    echo -e "  ${FAIL} ${name} ${RED}${detail}${NC}"
    EXIT_CODE=1
  else
    echo -e "  ${SKIP} ${name} ${YELLOW}${detail}${NC}"
  fi
}

echo ""
echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║              ReminderBot Pro - Health Check                  ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
if [[ -f "${PROJECT_ROOT}/.env" ]]; then
  set -a
  source "${PROJECT_ROOT}/.env"
  set +a
fi

TIMEOUT=10

# ─── Backend ───────────────────────────────────────────────────────────────

echo -e " ${BLUE}Backend${NC}"
BACKEND_URL="${BACKEND_URL:-http://localhost:8000}"

if health=$(curl -sS --max-time "$TIMEOUT" "${BACKEND_URL}/api/v1/health" 2>/dev/null); then
  api_status=$(echo "$health" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('status','unknown'))" 2>/dev/null || echo "unknown")
  db_status=$(echo "$health" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('database','unknown'))" 2>/dev/null || echo "unknown")
  redis_status=$(echo "$health" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('redis','unknown'))" 2>/dev/null || echo "unknown")
  version=$(echo "$health" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('version','?'))" 2>/dev/null || echo "?")

  check "API Server" "pass" "v${version} | status: ${api_status}"
  check "Database" "pass" "${db_status}" 2>/dev/null
  check "Redis" "pass" "${redis_status}" 2>/dev/null
else
  check "API Server" "fail" "unreachable at ${BACKEND_URL}"
  check "Database" "fail" "skipped"
  check "Redis" "fail" "skipped"
fi

# ─── Frontend ──────────────────────────────────────────────────────────────

echo -e " ${BLUE}Frontend${NC}"
FRONTEND_URL="${FRONTEND_URL:-http://localhost:3000}"

if curl -sS --max-time "$TIMEOUT" -o /dev/null -w "%{http_code}" "${FRONTEND_URL}" 2>/dev/null | grep -q "200\|302"; then
  check "Web App" "pass" "responding at ${FRONTEND_URL}"
else
  check "Web App" "fail" "unreachable at ${FRONTEND_URL}"
fi

# ─── Database (direct) ─────────────────────────────────────────────────────

echo -e " ${BLUE}Database${NC}"
PG_HOST="${PG_HOST:-localhost}"
PG_PORT="${PG_PORT:-5432}"
PG_USER="${PG_USER:-reminderbot}"
PG_DATABASE="${PG_DATABASE:-reminderbot}"

if command -v pg_isready &>/dev/null; then
  if pg_isready -h "$PG_HOST" -p "$PG_PORT" -q 2>/dev/null; then
    db_size=$(PGPASSWORD="${PG_PASSWORD}" psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$PG_DATABASE" -t -c "SELECT pg_size_pretty(pg_database_size('${PG_DATABASE}'))" 2>/dev/null | tr -d ' ')
    conn_count=$(PGPASSWORD="${PG_PASSWORD}" psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$PG_DATABASE" -t -c "SELECT count(*) FROM pg_stat_activity WHERE datname='${PG_DATABASE}'" 2>/dev/null | tr -d ' ')
    check "PostgreSQL" "pass" "size: ${db_size:-?} | connections: ${conn_count:-?}"
  else
    check "PostgreSQL" "fail" "not accepting connections"
  fi
else
  check "PostgreSQL" "skip" "pg_isready not installed"
fi

# ─── Redis (direct) ────────────────────────────────────────────────────────

echo -e " ${BLUE}Redis${NC}"
REDIS_HOST="${REDIS_HOST:-localhost}"
REDIS_PORT="${REDIS_PORT:-6379}"

if command -v redis-cli &>/dev/null; then
  if redis_ping=$(redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" ping 2>/dev/null); then
    redis_mem=$(redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" info memory 2>/dev/null | grep "used_memory_human:" | cut -d: -f2 | tr -d '\r')
    redis_uptime=$(redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" info server 2>/dev/null | grep "uptime_in_days:" | cut -d: -f2 | tr -d '\r')
    check "Redis" "pass" "memory: ${redis_mem:-?} | uptime: ${redis_uptime:-?}d"
  else
    check "Redis" "fail" "not responding"
  fi
else
  check "Redis" "skip" "redis-cli not installed"
fi

# ─── Celery ────────────────────────────────────────────────────────────────

echo -e " ${BLUE}Celery${NC}"
CELERY_BROKER_URL="${CELERY_BROKER_URL:-redis://localhost:6379/1}"

if command -v celery &>/dev/null; then
  if celery_status=$(celery -A app.core.celery_app inspect ping --timeout=5 2>/dev/null); then
    check "Celery Worker" "pass" "responds to ping"
  else
    check "Celery Worker" "fail" "no active workers"
  fi
elif curl -sS --max-time 5 "${BACKEND_URL}/api/v1/health/celery" 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('status','unknown'))" 2>/dev/null | grep -q "ok"; then
  check "Celery Worker" "pass" "via API"
else
  check "Celery Worker" "skip" "celery CLI not available and API check failed"
fi

# ─── Summary ───────────────────────────────────────────────────────────────

echo ""
if [[ "$EXIT_CODE" -eq 0 ]]; then
  echo -e "${GREEN}All checks passed!${NC}"
else
  echo -e "${RED}Some checks failed!${NC}"
fi
echo ""

exit $EXIT_CODE

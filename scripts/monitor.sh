#!/usr/bin/env bash
set -euo pipefail

# ─── ReminderBot Pro - Monitoring Script ──────────────────────────────────────
# Reports all service health and metrics to stdout.
# Can be used as a cron job or integrated with external monitoring.

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
if [[ -f "${PROJECT_ROOT}/.env" ]]; then
  set -a
  source "${PROJECT_ROOT}/.env"
  set +a
fi

BACKEND_URL="${BACKEND_URL:-http://localhost:8000}"
FRONTEND_URL="${FRONTEND_URL:-http://localhost:3000}"
TIMEOUT=5

echo "reminderbot_monitor timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)"

# Backend health
if health=$(curl -sS --max-time "$TIMEOUT" "${BACKEND_URL}/api/v1/health" 2>/dev/null); then
  api_status=$(echo "$health" | python3 -c "import sys,json; print(json.load(sys.stdin).get('status','down'))" 2>/dev/null || echo "down")
  echo "reminderbot_backend_status{type=\"api\"} $( [[ "$api_status" == "ok" ]] && echo 1 || echo 0)"
  echo "reminderbot_backend_status{type=\"database\"} $(echo "$health" | python3 -c "import sys,json; print(1 if json.load(sys.stdin).get('database')=='connected' else 0)" 2>/dev/null || echo 0)"
  echo "reminderbot_backend_status{type=\"redis\"} $(echo "$health" | python3 -c "import sys,json; print(1 if json.load(sys.stdin).get('redis')=='connected' else 0)" 2>/dev/null || echo 0)"
else
  echo "reminderbot_backend_status{type=\"api\"} 0"
  echo "reminderbot_backend_status{type=\"database\"} 0"
  echo "reminderbot_backend_status{type=\"redis\"} 0"
fi

# Frontend health
frontend_code=$(curl -sS --max-time "$TIMEOUT" -o /dev/null -w "%{http_code}" "${FRONTEND_URL}" 2>/dev/null || echo "000")
echo "reminderbot_frontend_status $( [[ "$frontend_code" == "200" || "$frontend_code" == "302" ]] && echo 1 || echo 0)"

# Database metrics
if command -v psql &>/dev/null; then
  PG_HOST="${PG_HOST:-localhost}"
  PG_PORT="${PG_PORT:-5432}"
  PG_USER="${PG_USER:-reminderbot}"
  PG_DATABASE="${PG_DATABASE:-reminderbot}"

  conn_count=$(PGPASSWORD="${PG_PASSWORD:-}" psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$PG_DATABASE" -t -c "SELECT count(*) FROM pg_stat_activity WHERE datname='${PG_DATABASE}'" 2>/dev/null | tr -d ' ' || echo "0")
  db_size=$(PGPASSWORD="${PG_PASSWORD:-}" psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$PG_DATABASE" -t -c "SELECT pg_database_size('${PG_DATABASE}')" 2>/dev/null | tr -d ' ' || echo "0")
  echo "reminderbot_db_connections $conn_count"
  echo "reminderbot_db_size_bytes $db_size"
fi

# Redis metrics
if command -v redis-cli &>/dev/null; then
  REDIS_HOST="${REDIS_HOST:-localhost}"
  REDIS_PORT="${REDIS_PORT:-6379}"

  redis_ping=$(redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" ping 2>/dev/null || echo "FAIL")
  if [[ "$redis_ping" == "PONG" ]]; then
    echo "reminderbot_redis_status 1"
    used_mem=$(redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" info memory 2>/dev/null | grep "used_memory:" | cut -d: -f2 | tr -d '\r' || echo "0")
    total_keys=$(redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" info keyspace 2>/dev/null | grep "^db0:" | sed 's/.*keys=\([0-9]*\).*/\1/' || echo "0")
    echo "reminderbot_redis_memory_bytes $used_mem"
    echo "reminderbot_redis_keys $total_keys"
  else
    echo "reminderbot_redis_status 0"
  fi
fi

# Reminder counts (via API)
if reminder_stats=$(curl -sS --max-time "$TIMEOUT" "${BACKEND_URL}/api/v1/reminders/stats" 2>/dev/null); then
  active_count=$(echo "$reminder_stats" | python3 -c "import sys,json; print(json.load(sys.stdin).get('active_count',0))" 2>/dev/null || echo "0")
  overdue_count=$(echo "$reminder_stats" | python3 -c "import sys,json; print(json.load(sys.stdin).get('overdue_count',0))" 2>/dev/null || echo "0")
  completed_today=$(echo "$reminder_stats" | python3 -c "import sys,json; print(json.load(sys.stdin).get('completed_today',0))" 2>/dev/null || echo "0")
  echo "reminderbot_reminders_active $active_count"
  echo "reminderbot_reminders_overdue $overdue_count"
  echo "reminderbot_reminders_completed_today $completed_today"
fi

# System metrics
if [[ -f /proc/loadavg ]]; then
  read -r load1 load5 load15 _ _ < /proc/loadavg
  echo "reminderbot_system_load_1m $load1"
  echo "reminderbot_system_load_5m $load5"
  echo "reminderbot_system_load_15m $load15"
fi

if [[ -f /proc/meminfo ]]; then
  mem_total=$(grep MemTotal /proc/meminfo | awk '{print $2}')
  mem_avail=$(grep MemAvailable /proc/meminfo | awk '{print $2}')
  echo "reminderbot_system_mem_total_kb $mem_total"
  echo "reminderbot_system_mem_avail_kb $mem_avail"
fi

# Summary
echo "reminderbot_monitor_status 1"

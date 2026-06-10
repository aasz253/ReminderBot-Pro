#!/usr/bin/env bash
set -euo pipefail

# ─── ReminderBot Pro - Database Restore Script ───────────────────────────────

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info()  { echo -e "${BLUE}[INFO]${NC}  $*"; }
log_ok()    { echo -e "${GREEN}[OK]${NC}    $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $*"; }

# ─── Usage ──────────────────────────────────────────────────────────────────

usage() {
  echo "Usage: $0 [options] <backup_file>"
  echo ""
  echo "Restore a ReminderBot Pro database from backup."
  echo ""
  echo "Options:"
  echo "  -h, --host <host>      Database host (default: localhost)"
  echo "  -p, --port <port>      Database port (default: 5432)"
  echo "  -U, --user <user>      Database user (default: reminderbot)"
  echo "  -d, --dbname <db>      Database name (default: reminderbot)"
  echo "  -f, --force            Skip confirmation prompt"
  echo "  --help                 Show this help message"
  echo ""
  echo "Examples:"
  echo "  $0 backups/reminderbot_20240101_120000.sql.gz"
  echo "  $0 -h prod-db.example.com -U admin -d reminderbot backups/latest.sql.gz"
  exit 1
}

# ─── Parse Arguments ────────────────────────────────────────────────────────

FORCE=false
PG_HOST="localhost"
PG_PORT="5432"
PG_USER="reminderbot"
PG_DATABASE="reminderbot"

while [[ $# -gt 0 ]]; do
  case $1 in
    -h|--host) PG_HOST="$2"; shift 2 ;;
    -p|--port) PG_PORT="$2"; shift 2 ;;
    -U|--user) PG_USER="$2"; shift 2 ;;
    -d|--dbname) PG_DATABASE="$2"; shift 2 ;;
    -f|--force) FORCE=true; shift ;;
    --help) usage ;;
    -*)
      echo "Unknown option: $1"
      usage
      ;;
    *)
      BACKUP_FILE="$1"
      shift
      ;;
  esac
done

if [[ -z "${BACKUP_FILE:-}" ]]; then
  log_error "No backup file specified"
  usage
fi

if [[ ! -f "$BACKUP_FILE" ]]; then
  log_error "Backup file not found: ${BACKUP_FILE}"
  exit 1
fi

# ─── Prerequisites ─────────────────────────────────────────────────────────

if ! command -v pg_restore &>/dev/null; then
  log_error "pg_restore not found. Install postgresql-client."
  exit 1
fi

# ─── Confirmation ──────────────────────────────────────────────────────────

echo ""
echo -e "${RED}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${RED}║                    DANGER ZONE                              ║${NC}"
echo -e "${RED}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "This will DESTROY the current database and replace it with the backup."
echo ""
echo "  Database: ${PG_DATABASE}"
echo "  Host:     ${PG_HOST}:${PG_PORT}"
echo "  User:     ${PG_USER}"
echo "  Backup:   ${BACKUP_FILE}"
echo ""

if [[ "$FORCE" != "true" ]]; then
  read -rp "Are you sure you want to continue? (type 'yes' to confirm): " CONFIRM
  if [[ "$CONFIRM" != "yes" ]]; then
    echo "Restore cancelled."
    exit 0
  fi
fi

# ─── Restore ───────────────────────────────────────────────────────────────

log_info "Starting restore..."
log_info "Source backup: ${BACKUP_FILE}"
log_info "Target database: ${PG_DATABASE}@${PG_HOST}:${PG_PORT}"

# Get password if set
PGPASSWORD="${PG_PASSWORD:-}"
if [[ -f "${PROJECT_ROOT:-.}/.env" ]]; then
  set -a
  source "${PROJECT_ROOT:-.}/.env"
  set +a
fi
export PGPASSWORD

# Determine file type and restore
FILE_EXT="${BACKUP_FILE##*.}"

if [[ "$FILE_EXT" == "gz" ]]; then
  # Compressed file - decompress and restore
  log_info "Decompressing and restoring..."

  # Terminate active connections first
  psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "postgres" -c "
    SELECT pg_terminate_backend(pg_stat_activity.pid)
    FROM pg_stat_activity
    WHERE pg_stat_activity.datname = '${PG_DATABASE}'
      AND pid <> pg_backend_pid();
  " 2>/dev/null || true

  # Drop and recreate database
  psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "postgres" -c "DROP DATABASE IF EXISTS ${PG_DATABASE};" 2>/dev/null || true
  psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "postgres" -c "CREATE DATABASE ${PG_DATABASE};"

  # Restore
  if [[ "$BACKUP_FILE" == *.dump.gz ]]; then
    gunzip -c "$BACKUP_FILE" | pg_restore \
      --host="$PG_HOST" \
      --port="$PG_PORT" \
      --username="$PG_USER" \
      --dbname="$PG_DATABASE" \
      --no-owner \
      --no-acl \
      --verbose \
      --jobs=4
  else
    gunzip -c "$BACKUP_FILE" | psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$PG_DATABASE" -v ON_ERROR_STOP=1
  fi
else
  # Raw SQL or custom format
  pg_restore \
    --host="$PG_HOST" \
    --port="$PG_PORT" \
    --username="$PG_USER" \
    --dbname="$PG_DATABASE" \
    --no-owner \
    --no-acl \
    --verbose \
    --jobs=4 \
    "$BACKUP_FILE"
fi

log_ok "Restore completed successfully!"

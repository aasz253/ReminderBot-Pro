#!/usr/bin/env bash
set -euo pipefail

# ─── ReminderBot Pro - Database Backup Script ────────────────────────────────

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info()  { echo -e "${BLUE}[INFO]${NC}  $*"; }
log_ok()    { echo -e "${GREEN}[OK]${NC}    $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $*"; }

# ─── Configuration ──────────────────────────────────────────────────────────

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACKUP_DIR="${BACKUP_DIR:-${PROJECT_ROOT}/backups}"
RETENTION_DAYS="${RETENTION_DAYS:-7}"

# Database connection (from env or .env)
if [[ -f "${PROJECT_ROOT}/.env" ]]; then
  set -a
  source "${PROJECT_ROOT}/.env"
  set +a
fi

PG_HOST="${PG_HOST:-localhost}"
PG_PORT="${PG_PORT:-5432}"
PG_USER="${PG_USER:-reminderbot}"
PG_PASSWORD="${PG_PASSWORD:-reminderbot_secret}"
PG_DATABASE="${PG_DATABASE:-reminderbot}"

S3_BUCKET="${S3_BUCKET:-}"
S3_PREFIX="${S3_PREFIX:-backups/reminderbot}"
AWS_PROFILE="${AWS_PROFILE:-default}"

SLACK_WEBHOOK_URL="${SLACK_WEBHOOK_URL:-}"

# ─── Prerequisites ─────────────────────────────────────────────────────────

if ! command -v pg_dump &>/dev/null; then
  log_error "pg_dump not found. Install postgresql-client."
  exit 1
fi

if [[ -n "$S3_BUCKET" ]] && ! command -v aws &>/dev/null; then
  log_error "S3 configured but aws CLI not found."
  exit 1
fi

mkdir -p "$BACKUP_DIR"

# ─── Backup ────────────────────────────────────────────────────────────────

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/reminderbot_${TIMESTAMP}.sql.gz"
LOG_FILE="${BACKUP_DIR}/backup_${TIMESTAMP}.log"

log_info "Starting backup..."
log_info "Database: ${PG_DATABASE}@${PG_HOST}:${PG_PORT}"
log_info "Output: ${BACKUP_FILE}"

export PGPASSWORD="${PG_PASSWORD}"

pg_dump \
  --host="${PG_HOST}" \
  --port="${PG_PORT}" \
  --username="${PG_USER}" \
  --dbname="${PG_DATABASE}" \
  --format=custom \
  --verbose \
  --no-owner \
  --no-acl \
  2>"$LOG_FILE" | gzip > "$BACKUP_FILE"

BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
log_ok "Backup created: ${BACKUP_FILE} (${BACKUP_SIZE})"

# ─── Upload to S3 ──────────────────────────────────────────────────────────

if [[ -n "$S3_BUCKET" ]]; then
  S3_PATH="s3://${S3_BUCKET}/${S3_PREFIX}/reminderbot_${TIMESTAMP}.sql.gz"
  log_info "Uploading to S3: ${S3_PATH}"

  if aws s3 cp "$BACKUP_FILE" "$S3_PATH" --profile "$AWS_PROFILE" --storage-class STANDARD_IA; then
    log_ok "Upload to S3 complete"
  else
    log_error "S3 upload failed"
  fi
fi

# ─── Retention Policy ──────────────────────────────────────────────────────

log_info "Cleaning backups older than ${RETENTION_DAYS} days..."
find "$BACKUP_DIR" -name "reminderbot_*.sql.gz" -type f -mtime "+${RETENTION_DAYS}" -delete
find "$BACKUP_DIR" -name "backup_*.log" -type f -mtime "+${RETENTION_DAYS}" -delete

if [[ -n "$S3_BUCKET" ]]; then
  # List old S3 backups and remove them
  CUTOFF_DATE=$(date -d "-${RETENTION_DAYS} days" +%Y-%m-%d)
  aws s3api list-objects \
    --bucket "$S3_BUCKET" \
    --prefix "${S3_PREFIX}/" \
    --query "Contents[?LastModified<='${CUTOFF_DATE}T00:00:00Z'].{Key: Key}" \
    --output text \
    --profile "$AWS_PROFILE" | while read -r key; do
      if [[ -n "$key" ]]; then
        aws s3 rm "s3://${S3_BUCKET}/${key}" --profile "$AWS_PROFILE"
        log_info "Removed old S3 backup: ${key}"
      fi
    done
fi

log_ok "Retention cleanup complete"

# ─── Notification ──────────────────────────────────────────────────────────

NOTIFICATION_TEXT="✅ ReminderBot Pro backup complete\n• File: ${BACKUP_FILE}\n• Size: ${BACKUP_SIZE}\n• Database: ${PG_DATABASE}"

if [[ -n "$SLACK_WEBHOOK_URL" ]]; then
  curl -s -X POST "$SLACK_WEBHOOK_URL" \
    -H "Content-Type: application/json" \
    -d "{\"text\": \"${NOTIFICATION_TEXT}\"}" \
    >/dev/null
  log_ok "Slack notification sent"
fi

log_ok "Backup complete: ${BACKUP_FILE} (${BACKUP_SIZE})"

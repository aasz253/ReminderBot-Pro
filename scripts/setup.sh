#!/usr/bin/env bash
set -euo pipefail

# ─── ReminderBot Pro Setup Script ─────────────────────────────────────────────

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info()  { echo -e "${BLUE}[INFO]${NC}  $*"; }
log_ok()    { echo -e "${GREEN}[OK]${NC}    $*"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $*"; }

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

# ─── Prerequisites ──────────────────────────────────────────────────────────

log_info "Checking prerequisites..."

check_python() {
  if command -v python3 &>/dev/null; then
    local pyver
    pyver=$(python3 --version 2>&1 | awk '{print $2}')
    local major minor
    major=$(echo "$pyver" | cut -d. -f1)
    minor=$(echo "$pyver" | cut -d. -f2)
    if [[ "$major" -ge 3 && "$minor" -ge 11 ]]; then
      log_ok "Python $pyver found"
      return 0
    fi
  fi
  log_error "Python 3.11+ required. Install it first."
  exit 1
}

check_node() {
  if command -v node &>/dev/null; then
    local nodever
    nodever=$(node --version 2>&1 | sed 's/v//')
    local major
    major=$(echo "$nodever" | cut -d. -f1)
    if [[ "$major" -ge 20 ]]; then
      log_ok "Node.js $nodever found"
      return 0
    fi
  fi
  log_warn "Node.js 20+ recommended. Install it from https://nodejs.org"
}

check_docker() {
  if command -v docker &>/dev/null && docker compose version &>/dev/null; then
    log_ok "Docker + Docker Compose found"
    return 0
  fi
  log_warn "Docker not found. Install from https://docs.docker.com/get-docker/"
}

check_python
check_node
check_docker

# ─── Setup ──────────────────────────────────────────────────────────────────

log_info "Creating Python virtual environment..."
if [[ ! -d .venv ]]; then
  python3 -m venv .venv
  log_ok "Virtual environment created"
else
  log_ok "Virtual environment already exists"
fi

source .venv/bin/activate

log_info "Installing backend dependencies..."
pip install --upgrade pip setuptools wheel
pip install -r backend/requirements.txt -r backend/requirements-dev.txt
log_ok "Backend dependencies installed"

log_info "Installing frontend dependencies..."
cd frontend
npm ci
cd "$PROJECT_ROOT"
log_ok "Frontend dependencies installed"

# ─── Configuration ──────────────────────────────────────────────────────────

if [[ ! -f .env ]]; then
  log_info "Creating .env from .env.production.example..."
  cp .env.production.example .env
  log_warn "Please edit .env with your configuration"
else
  log_ok ".env already exists"
fi

# ─── Database ───────────────────────────────────────────────────────────────

log_info "Running database migrations..."
cd backend
alembic upgrade head
cd "$PROJECT_ROOT"
log_ok "Migrations applied"

log_info "Creating superuser..."
cd backend
python -m scripts.create_superuser --email admin@reminderbot.com --password admin123 --skip-if-exists 2>/dev/null || true
cd "$PROJECT_ROOT"
log_ok "Superuser created (admin@reminderbot.com / admin123)"

log_info "Seeding default categories..."
cd backend
python -m scripts.seed 2>/dev/null || true
cd "$PROJECT_ROOT"
log_ok "Default data seeded"

# ─── Success ────────────────────────────────────────────────────────────────

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║          ReminderBot Pro - Setup Complete!                 ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  ${BLUE}Backend API:${NC}      http://localhost:8000"
echo -e "  ${BLUE}API Docs:${NC}         http://localhost:8000/docs"
echo -e "  ${BLUE}Frontend:${NC}         http://localhost:3000"
echo -e ""
echo -e "  ${YELLOW}Admin Login:${NC}      admin@reminderbot.com / admin123"
echo -e ""
echo -e "  Run ${GREEN}make dev${NC} to start the development environment"
echo -e "  Run ${GREEN}make docker-up${NC} to start with Docker"
echo ""

# ─── Cleanup ────────────────────────────────────────────────────────────────

deactivate 2>/dev/null || true

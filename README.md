# ReminderBot Pro

> Smart Reminder Management SaaS — Never forget what matters.

## Features

- **Multi-channel Notifications** — Email, SMS, and push notifications
- **Smart Scheduling** — Recurring reminders with natural language parsing
- **Category Management** — Organize reminders with color-coded categories
- **Real-time Sync** — WebSocket-based live updates across devices
- **Team Collaboration** — Share reminders and workspaces (Business plan)
- **Calendar Integration** — Google Calendar, Outlook sync
- **Analytics** — Track your reminder completion rates and patterns
- **API-first** — Full REST API for custom integrations
- **Webhooks** — Real-time event notifications for external services

## Tech Stack

### Backend
- **Python** 3.11+ / **FastAPI**
- **SQLAlchemy** 2.0 (async) + **Alembic**
- **Celery** + **Redis** (task queue & scheduler)
- **PostgreSQL** 16
- **Stripe** (payments)

### Frontend
- **Next.js** 14 (App Router)
- **TypeScript** / **TailwindCSS**
- **React Query** / **Zustand**
- **shadcn/ui** component library

### Infrastructure
- **Docker** + **Docker Compose**
- **Terraform** (DigitalOcean / AWS)
- **GitHub Actions** (CI/CD)
- **Prometheus** + **Grafana** (monitoring)
- **Nginx** (reverse proxy, SSL)

## Quick Start (Docker)

```bash
git clone https://github.com/yourorg/reminderbot-pro.git
cd reminderbot-pro

# Set up environment
cp .env.production.example .env
# Edit .env with your settings

# Start all services
docker compose -f infra/docker/docker-compose.yml up -d

# Run migrations
docker compose exec backend alembic upgrade head

# Seed default data
docker compose exec backend python -m scripts.seed

# Open in browser
open http://localhost:3000
```

## Development Setup

```bash
# Automated setup
./scripts/setup.sh

# Or manual:
make install
make dev
```

## Project Structure

```
reminderbot-pro/
├── backend/                  # FastAPI backend
│   ├── app/
│   │   ├── api/             # Route handlers
│   │   ├── core/            # Config, Celery, security
│   │   ├── models/          # SQLAlchemy models
│   │   ├── schemas/         # Pydantic schemas
│   │   └── services/        # Business logic
│   ├── migrations/          # Alembic migrations
│   ├── tests/               # Test suite
│   └── Dockerfile
├── frontend/                 # Next.js frontend
│   ├── src/
│   │   ├── app/            # App Router pages
│   │   ├── components/     # React components
│   │   ├── lib/            # Utilities & API client
│   │   └── hooks/          # Custom React hooks
│   └── Dockerfile
├── infra/
│   ├── docker/             # Docker Compose files
│   ├── nginx/              # Nginx config & SSL
│   ├── monitoring/         # Prometheus & Grafana
│   └── terraform/          # Infrastructure as Code
├── scripts/                 # Utility scripts
├── docs/                    # Documentation
├── .github/
│   └── workflows/          # CI/CD pipelines
└── Makefile
```

## Documentation

| Document | Description |
|----------|-------------|
| [Architecture](docs/ARCHITECTURE.md) | System design and component overview |
| [API Reference](docs/API.md) | Complete API documentation |
| [Deployment Guide](docs/DEPLOYMENT.md) | Production deployment instructions |

## Commands

```bash
make install      # Install all dependencies
make dev          # Start development environment
make build        # Build Docker images
make test         # Run tests
make lint         # Run linters
make migrate      # Run database migrations
make docker-up    # Start Docker Compose stack
make docker-down  # Stop Docker Compose stack
make seed         # Seed default data
make backup       # Backup database
make restore      # Restore database from backup
```

## License

MIT License — See [LICENSE](LICENSE) for details.

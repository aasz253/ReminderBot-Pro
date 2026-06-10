# ReminderBot Pro - Deployment Guide

## Prerequisites

### Required Tools
- **Python** 3.11 or higher
- **Node.js** 20 or higher
- **Docker** & **Docker Compose** v2
- **PostgreSQL** 16 (for local development without Docker)
- **Redis** 7 (for local development without Docker)
- **Git**

### Optional Tools
- **Terraform** 1.5+ (infrastructure provisioning)
- **AWS CLI** or **doctl** (cloud management)
- **kubectl** (if using Kubernetes)
- **Vercel CLI** (frontend deployment)

### Cloud Accounts
- **Container Registry**: GitHub Container Registry (GHCR), Docker Hub, or DO Container Registry
- **Database**: Railway, Render, DigitalOcean Managed DB, or AWS RDS
- **Cache**: Railway, Render, DigitalOcean Managed Redis, or AWS ElastiCache
- **Domain**: Namecheap, Cloudflare, or any DNS provider

---

## Local Development Setup

### 1. Clone and Configure
```bash
git clone https://github.com/yourorg/reminderbot-pro.git
cd reminderbot-pro
cp .env.production.example .env
# Edit .env with your local settings
```

### 2. Using Docker (Recommended)
```bash
# Start all services
docker compose -f infra/docker/docker-compose.yml -f infra/docker/docker-compose.dev.yml up -d

# Run migrations
docker compose exec backend alembic upgrade head

# Seed data
docker compose exec backend python -m scripts.seed

# View logs
docker compose logs -f
```

### 3. Without Docker
```bash
# Backend
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt -r backend/requirements-dev.txt
cd backend && alembic upgrade head && uvicorn app.main:app --reload --port 8000

# Frontend (separate terminal)
cd frontend && npm ci && npm run dev

# Celery (separate terminal)
cd backend && celery -A app.core.celery_app worker --loglevel=debug

# Celery Beat (separate terminal)
cd backend && celery -A app.core.celery_app beat --loglevel=debug
```

### 4. Verify
```bash
# Health check
curl http://localhost:8000/api/v1/health

# API Docs
open http://localhost:8000/docs

# Frontend
open http://localhost:3000
```

---

## Docker Deployment

### Build Images
```bash
# Backend
docker build -t ghcr.io/yourorg/reminderbot-backend:latest backend/

# Frontend
docker build -t ghcr.io/yourorg/reminderbot-frontend:latest frontend/
```

### Production Deploy
```bash
# Set environment variables
export SECRET_KEY=$(openssl rand -hex 32)
export DOMAIN=reminderbot.example.com

# Start stack
docker compose -f infra/docker/docker-compose.yml up -d

# Run migrations
docker compose exec backend alembic upgrade head

# Seed data (first time only)
docker compose exec backend python -m scripts.seed

# Check health
docker compose exec nginx curl http://localhost/api/v1/health
```

### Monitoring Stack
```bash
docker compose -f infra/docker/docker-compose.monitoring.yml up -d
# Grafana: http://localhost:3001 (admin/admin)
# Prometheus: http://localhost:9090
```

---

## Railway Deployment

### Prerequisites
- Railway account
- `RAILWAY_TOKEN` added to GitHub secrets
- Railway CLI: `npm i -g @railway/cli`

### Steps
```bash
# Login
railway login

# Link project
railway link

# Deploy
railway up

# Run migrations
railway run alembic upgrade head

# Set custom domain
railway domain --service backend api.reminderbot.example.com
railway domain --service frontend reminderbot.example.com
```

### Environment Variables
Set in Railway dashboard or via CLI:
```bash
railway variables set SECRET_KEY=$(openssl rand -hex 32)
railway variables set ENVIRONMENT=production
railway variables set SENTRY_DSN=your-sentry-dsn
```

---

## Render Deployment

### Blueprint (Infrastructure as Code)
1. Push to GitHub
2. Connect repository to Render
3. Render Blueprint auto-detects `render.yaml`

### Manual Setup
1. Create a **Web Service** for Backend
   - Runtime: Docker
   - Port: 8000
   - Health Check Path: `/api/v1/health`
2. Create a **Web Service** for Frontend
   - Runtime: Docker
   - Port: 3000
3. Create a **PostgreSQL** database
4. Create a **Redis** instance
5. Configure environment variables
6. Run migrations via Render Shell

---

## Vercel Deployment (Frontend)

### Vercel Config
```json
// vercel.json
{
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "framework": "nextjs",
  "env": {
    "NEXT_PUBLIC_API_URL": "https://api.reminderbot.example.com",
    "NEXT_PUBLIC_WS_URL": "wss://api.reminderbot.example.com/ws"
  }
}
```

### Deploy
```bash
# Via Vercel CLI
vercel --prod

# Or connect GitHub repo in Vercel dashboard
```

---

## Production Checklist

### Pre-Launch
- [ ] Domain configured with DNS A/AAAA records pointing to load balancer
- [ ] SSL certificates issued (Let's Encrypt)
- [ ] Environment variables set for all services
- [ ] Database migrations run
- [ ] Redis configured with persistence
- [ ] CORS origins configured
- [ ] Rate limiting configured
- [ ] Monitoring stack deployed
- [ ] Backups configured (cron + S3)
- [ ] Sentry DSN configured for error tracking
- [ ] Stripe webhook endpoints registered
- [ ] Email provider (SMTP) configured and tested
- [ ] SMS provider (Twilio) configured (if using)
- [ ] Push notifications (Pushover) configured (if using)

### Security
- [ ] Strong SECRET_KEY generated (64+ chars)
- [ ] Database passwords rotated from defaults
- [ ] HTTPS enforced (HTTP -> 301 redirect)
- [ ] Security headers set (HSTS, CSP, etc.)
- [ ] API rate limiting enabled
- [ ] Docker images scanned for vulnerabilities
- [ ] Secrets detection configured in CI
- [ ] Regular dependency updates via Dependabot
- [ ] Database firewall rules set (private network only)

### Monitoring
- [ ] Grafana dashboards imported
- [ ] Alert rules configured
- [ ] Slack/Telegram notifications set up
- [ ] Uptime monitoring (e.g., BetterStack, Pingdom)
- [ ] Log aggregation configured

---

## Environment Variables Reference

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `SECRET_KEY` | Yes | Django/FastAPI secret key (64 chars) | - |
| `DATABASE_URL` | Yes | PostgreSQL async connection string | - |
| `REDIS_URL` | Yes | Redis connection string | - |
| `CELERY_BROKER_URL` | Yes | Celery broker URL | - |
| `CELERY_RESULT_BACKEND` | Yes | Celery result backend URL | - |
| `ENVIRONMENT` | Yes | production/development/testing | production |
| `LOG_LEVEL` | No | debug/info/warning/error | info |
| `FRONTEND_URL` | Yes | Frontend URL for CORS | - |
| `CORS_ORIGINS` | Yes | Allowed CORS origins | - |
| `SENTRY_DSN` | No | Sentry error tracking DSN | - |
| `SMTP_HOST` | Yes* | SMTP server host | - |
| `SMTP_PORT` | Yes* | SMTP server port | 587 |
| `SMTP_USER` | Yes* | SMTP username | - |
| `SMTP_PASSWORD` | Yes* | SMTP password | - |
| `TWILIO_ACCOUNT_SID` | No | Twilio account SID | - |
| `TWILIO_AUTH_TOKEN` | No | Twilio auth token | - |
| `TWILIO_PHONE_NUMBER` | No | Twilio phone number | - |
| `STRIPE_SECRET_KEY` | Yes* | Stripe secret key | - |
| `STRIPE_WEBHOOK_SECRET` | Yes* | Stripe webhook signing secret | - |
| `NEXT_PUBLIC_API_URL` | Yes | Frontend API URL | - |
| `NEXT_PUBLIC_WS_URL` | Yes | Frontend WebSocket URL | - |

*\* Required if the corresponding feature is enabled*

---

## Database Migrations

### Commands
```bash
# Generate new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one step
alembic downgrade -1

# View history
alembic history

# Show current version
alembic current
```

### Production Migration
```bash
# Back up database first!
./scripts/backup.sh

# Apply migrations
alembic upgrade head

# Verify
alembic check
```

---

## SSL Setup

### With Certbot (Docker)
```bash
# Initial certificate
docker compose run --rm certbot certonly --webroot \
  --webroot-path=/var/www/certbot \
  -d reminderbot.example.com -d api.reminderbot.example.com

# Auto-renewal (cron)
0 3 * * * docker compose run --rm certbot renew --quiet --post-hook "nginx -s reload"
```

### With DigitalOcean Load Balancer
Managed SSL is configured via Terraform; certificates auto-renew.

---

## Monitoring Setup

### 1. Deploy Stack
```bash
docker compose -f infra/docker/docker-compose.monitoring.yml up -d
```

### 2. Configure Grafana
Import the pre-built dashboard from `infra/monitoring/grafana/dashboards/dashboard.json`. The Prometheus datasource is auto-configured.

### 3. Configure Alerts
Alert rules are defined in `infra/monitoring/prometheus/alerts.yml`. Modify thresholds as needed.

### 4. Notification Channels
Set up Slack/Telegram notifications in Alertmanager config.

---

## Backup & Restore

### Automatic Backups
Add to crontab:
```bash
# Daily backup at 2 AM
0 2 * * * /path/to/scripts/backup.sh
```

### Manual Backup
```bash
./scripts/backup.sh
# Creates timestamped backup in backups/
# Optionally uploads to S3 if S3_BUCKET is set
```

### Restore
```bash
# List available backups
ls -lh backups/

# Restore from backup
./scripts/restore.sh backups/reminderbot_20240101_120000.sql.gz

# Or with confirmation skip (for automation)
./scripts/restore.sh -f backups/latest.sql.gz
```

### Retention
Backups older than 7 days are automatically pruned. Adjust with `RETENTION_DAYS` env var.

---

## Scaling Guidelines

### When to Scale

| Metric | Threshold | Action |
|--------|-----------|--------|
| CPU > 80% (5 min) | 2 instances | Add backend replicas |
| Memory > 85% | 4GB | Increase instance size |
| P95 latency > 500ms | 5 min | Add backend replicas |
| Celery queue > 1000 | 10 min | Add worker instances |
| DB connections > 80% | 5 min | Increase pool size/replicas |
| Redis memory > 80% | 5 min | Increase Redis plan |

### Frontend Scaling
- Static assets served via CDN
- Multiple Next.js instances behind load balancer
- Redis session store for sticky sessions

### Backend Scaling
- Stateless design — add replicas behind Nginx
- Database connection pooling (min: 5, max: 20 per instance)
- Read replicas for reporting queries

### Database Scaling
- Vertical: Increase instance size (RAM > CPU)
- Horizontal: Read replicas for analytics
- Connection pooling with PgBouncer (optional)

### Celery Scaling
- Increase `--concurrency` up to 4x CPU cores
- Add worker instances for queue depth
- Separate queues by priority (critical, default, low)
- Task deduplication via Redis locks

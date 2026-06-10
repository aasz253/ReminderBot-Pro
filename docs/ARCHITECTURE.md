# ReminderBot Pro - Architecture

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                          Client Layer                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌───────────────────┐   │
│  │   Web    │  │  Mobile  │  │   API    │  │  3rd Party        │   │
│  │ (Next.js)│  │ (React   │  │ Clients  │  │  Webhooks/Integ.  │   │
│  │          │  │  Native) │  │ (REST)   │  │                   │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────────┬──────────┘   │
└───────┼──────────────┼─────────────┼──────────────────┼──────────────┘
        │              │             │                  │
┌───────┼──────────────┼─────────────┼──────────────────┼──────────────┐
│      ┌┴──────────────┴─────────────┴──────────────────┴────────┐     │
│      │              Reverse Proxy (Nginx)                       │     │
│      │  SSL Termination | Rate Limiting | Load Balancing       │     │
│      └──────────────────────┬──────────────────────────────────┘     │
│                             │                                        │
│      ┌──────────────────────┼──────────────────────────────────┐     │
│      │                      │                                  │     │
│      ▼                      ▼                                  ▼     │
│ ┌──────────┐          ┌──────────┐                       ┌────────┐  │
│ │ Frontend │          │  Backend │                       │  Web-   │  │
│ │ Next.js  │◄────────►│ FastAPI  │◄──────────────────────►│ sockets│  │
│ │ SSR/SPA  │  REST    │  (uvicon)│    WebSocket           │        │  │
│ └──────────┘          └────┬─────┘                       └────────┘  │
│                            │                                          │
│           ┌────────────────┼────────────────────┐                     │
│           ▼                ▼                    ▼                     │
│     ┌──────────┐    ┌──────────┐        ┌──────────────┐             │
│     │ Celery   │    │ Celery   │        │   Prometheus │             │
│     │ Worker   │    │  Beat    │        │   + Grafana  │             │
│     │ (Tasks)  │    │(Schedule)│        │ (Monitoring) │             │
│     └────┬─────┘    └──────────┘        └──────────────┘             │
│          │                                                           │
│     ┌────┴────────────────────┐                                      │
│     │         Redis           │                                      │
│     │  Cache | Queue | Session│                                      │
│     └────┬────────────────────┘                                      │
│          │                                                           │
│     ┌────┴────────────────────┐                                      │
│     │      PostgreSQL         │                                      │
│     │   Primary Database      │                                      │
│     └─────────────────────────┘                                      │
└──────────────────────────────────────────────────────────────────────┘
```

## Component Overview

### 1. Frontend (Next.js)
- **Framework**: Next.js 14 with App Router
- **Rendering**: Hybrid SSR + Client Components
- **State Management**: React Query for server state, Zustand for client state
- **UI**: TailwindCSS + shadcn/ui components
- **Real-time**: WebSocket connection for live reminder notifications
- **PWA**: Service worker for offline reminders

### 2. Backend (FastAPI)
- **Framework**: FastAPI with Python 3.11+
- **ORM**: SQLAlchemy 2.0 (async) with Alembic migrations
- **Validation**: Pydantic v2 for request/response schemas
- **Auth**: JWT tokens (access + refresh) with OAuth2 password flow
- **Background Tasks**: Celery with Redis broker
- **API Style**: RESTful with versioned endpoints (`/api/v1/`)
- **Docs**: Auto-generated OpenAPI/Swagger at `/docs`

### 3. Celery Workers
- **Task Queue**: Celery with Redis as broker and result backend
- **Periodic Tasks**: Celery Beat for scheduled reminders
- **Task Types**:
  - `send_reminder_notification` - Email/SMS/Push delivery
  - `process_recurring_reminder` - Handle recurring reminder logic
  - `cleanup_expired_reminders` - Daily maintenance
  - `generate_usage_report` - Weekly/monthly analytics

### 4. PostgreSQL
- **Version**: 16 with asyncpg driver
- **Extensions**: pgcrypto (UUIDs), pg_trgm (text search)
- **Connection Pool**: SQLAlchemy async pool (min: 5, max: 20)
- **Migrations**: Alembic with auto-generation

### 5. Redis
- **Version**: 7
- **Usage**: Celery broker (db 1), result backend (db 2), cache (db 0), sessions
- **Persistence**: AOF + RDB for durability

### 6. Nginx
- Reverse proxy with SSL termination
- Rate limiting per IP/endpoint
- Static asset caching
- WebSocket proxying

## Data Flow

### Reminder Creation Flow
```
User → Frontend → POST /api/v1/reminders → Backend validates → DB insert
  → Celery task scheduled → Confirmation response → User
```

### Reminder Notification Flow
```
Celery Beat ticks → Queries due reminders → Dispatches to Celery Worker
  → Worker checks user preferences → Sends Email/SMS/Push
  → Updates reminder status → Logs delivery attempt
```

### Authentication Flow
```
User → Login form → POST /api/v1/auth/login → Validate credentials
  → Generate JWT (access + refresh) → Return tokens → Store in HTTP-only cookie
  → Subsequent requests: Authorization: Bearer <token>
  → Token refresh via /api/v1/auth/refresh
```

### Payment Flow
```
User → Selects plan → POST /api/v1/subscriptions/create →
  → Stripe Checkout Session created → User redirected to Stripe →
  → Stripe webhook → Verify signature → Activate subscription →
  → Email confirmation → Update user's subscription tier
```

## Scaling Strategy

### Horizontal Scaling
- **Frontend**: Deploy multiple Next.js instances behind Nginx load balancer
- **Backend**: Stateless FastAPI — scale horizontally with Nginx least_conn
- **Celery Workers**: Increase worker count and concurrency based on queue depth
- **Database**: Read replicas for analytics queries, connection pooling

### Caching Strategy
- **Redis**: Session data, reminder counts, user preferences (TTL-based)
- **CDN**: Static assets (images, fonts) via CDN with 30-day cache
- **API Cache**: Response caching for non-sensitive GET endpoints

## Security Considerations

### Authentication & Authorization
- JWT with short-lived access tokens (15 min) + long-lived refresh (7 days)
- Refresh token rotation — old token invalidated on refresh
- Rate limiting on auth endpoints (5 attempts/15 min)
- bcrypt password hashing (cost factor 12)

### Data Protection
- All traffic encrypted with TLS 1.2+
- Database credentials stored in secrets manager
- PII encrypted at rest using PostgreSQL pgcrypto
- API keys for webhooks with rotation policy

### API Security
- CORS restricted to frontend origin
- Request size limited to 10MB
- SQL injection prevention via parameterized queries
- XSS protection via CSP headers
- CSRF protection via double-submit cookie pattern

### Infrastructure Security
- All services run in private VPC
- Database only accessible from app tier
- Regular security updates via CI/CD pipeline
- Secrets detection in CI
- Docker image scanning with Trivy

## Monitoring & Observability

### Metrics (Prometheus)
- Request rate, latency (P50/P95/P99), error rate
- Database connection pool usage, query performance
- Redis memory usage, hit rate, command rate
- Celery queue depth, task processing time
- System resources (CPU, memory, disk, network)

### Logging (Structured JSON)
- Centralized logging with log aggregation
- Request ID correlation across services
- Error tracking with Sentry
- Audit log for sensitive operations

### Alerting
- High API latency (>500ms P95)
- Error rate exceeds 5%
- Service down for >1 minute
- Database connection pool >80%
- Disk space <10%
- Celery queue growing beyond threshold

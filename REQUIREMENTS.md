# ReminderBot Pro — Product Requirements Document

> **Version:** 1.0.0  
> **Status:** Draft  
> **Last Updated:** 2026-06-10  

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Product Overview](#2-product-overview)
3. [User Personas](#3-user-personas)
4. [Functional Requirements](#4-functional-requirements)
5. [Non-Functional Requirements](#5-non-functional-requirements)
6. [User Stories](#6-user-stories)
7. [Feature Specifications](#7-feature-specifications)
8. [API Specifications](#8-api-specifications)
9. [Database Requirements](#9-database-requirements)
10. [Security Requirements](#10-security-requirements)
11. [Integration Requirements](#11-integration-requirements)
12. [Performance Requirements](#12-performance-requirements)
13. [Scalability Requirements](#13-scalability-requirements)
14. [Compliance & Legal](#14-compliance--legal)
15. [Acceptance Criteria](#15-acceptance-criteria)
16. [Glossary](#16-glossary)

---

## 1. Executive Summary

### 1.1 Purpose
ReminderBot Pro is a multi-channel reminder and notification SaaS platform that enables users to schedule reminders using natural language commands and receive notifications through their preferred communication channels (Telegram, WhatsApp, Email, SMS, Push).

### 1.2 Target Market
- **Primary:** Individual productivity users (students, professionals, freelancers)
- **Secondary:** Teams and small businesses requiring shared task management
- **Tertiary:** Enterprises needing white-label reminder solutions

### 1.3 Revenue Model
- Freemium SaaS with 3 tiers: Free, Premium ($3/mo), Business ($10/mo)
- Reminder template marketplace (commission-based)
- Affiliate program
- White-label licensing

### 1.4 Success Metrics
| Metric | Target (Year 1) |
|--------|-----------------|
| Registered Users | 100,000+ |
| Active Users (DAU) | 25,000+ |
| Premium Conversion | 5%+ |
| Reminder Delivery Rate | 99.5%+ |
| Average Response Time | <200ms |
| Monthly Revenue (MRR) | $50,000+ |

---

## 2. Product Overview

### 2.1 Problem Statement
Users struggle to remember tasks across multiple contexts (work, personal, health, finance). Existing reminder apps:
- Are single-channel (mobile-only, no Telegram/WhatsApp)
- Lack natural language input
- Don't support team collaboration
- Have limited or expensive notification options

### 2.2 Solution
A unified reminder platform that:
- Accepts natural language input ("remind me in 15 minutes")
- Delivers via 5+ channels simultaneously
- Supports recurring and one-time reminders
- Provides AI-powered suggestions
- Enables team collaboration
- Scales from free individual use to enterprise

### 2.3 Core Value Proposition
"Never miss what matters most — your reminders delivered wherever you are."

---

## 3. User Personas

### 3.1 Student — Sarah
- **Age:** 21
- **Needs:** Study reminders, assignment deadlines, exam schedule
- **Channels:** Telegram, Email
- **Pain Point:** Forgets deadlines without constant notifications
- **Plan:** Free → Premium

### 3.2 Professional — James
- **Age:** 34
- **Needs:** Meeting reminders, task follow-ups, recurring reports
- **Channels:** Email, WhatsApp, Push
- **Pain Point:** Misses meetings across time zones
- **Plan:** Premium

### 3.3 Freelancer — Amina
- **Age:** 28
- **Needs:** Client follow-ups, invoice reminders, project milestones
- **Channels:** WhatsApp, SMS, Telegram
- **Pain Point:** Juggling multiple clients and deadlines
- **Plan:** Premium

### 3.4 Business Owner — David
- **Age:** 42
- **Needs:** Team task assignment, deadline tracking, productivity reports
- **Channels:** All channels
- **Pain Point:** No oversight of team task completion
- **Plan:** Business

### 3.5 Admin — Technical Team
- **Needs:** User management, billing oversight, platform monitoring, support tickets

---

## 4. Functional Requirements

### FR1: User Authentication
| ID | Requirement | Priority |
|----|-------------|----------|
| FR1.1 | Email/password registration with verification | P0 |
| FR1.2 | Login with email + password | P0 |
| FR1.3 | Google OAuth login | P0 |
| FR1.4 | GitHub OAuth login | P1 |
| FR1.5 | Telegram login widget | P1 |
| FR1.6 | Password reset via email | P0 |
| FR1.7 | Two-factor authentication (TOTP) | P1 |
| FR1.8 | Session management (refresh tokens) | P0 |
| FR1.9 | Account deletion | P1 |

### FR2: Reminder Management
| ID | Requirement | Priority |
|----|-------------|----------|
| FR2.1 | Create reminder with title, time, priority, category | P0 |
| FR2.2 | Natural language input parsing | P0 |
| FR2.3 | Edit existing reminder | P0 |
| FR2.4 | Delete reminder | P0 |
| FR2.5 | Pause/resume reminder | P1 |
| FR2.6 | Mark reminder as complete | P0 |
| FR2.7 | One-time reminders | P0 |
| FR2.8 | Recurring reminders (daily/weekly/monthly/yearly/custom cron) | P0 |
| FR2.9 | Timezone-aware scheduling | P0 |
| FR2.10 | Bulk operations (multi-select, batch pause/delete/complete) | P1 |
| FR2.11 | Search/filter reminders by status, priority, category, date | P0 |
| FR2.12 | Category assignment and custom categories | P0 |

### FR3: Notification Delivery
| ID | Requirement | Priority |
|----|-------------|----------|
| FR3.1 | Telegram bot direct message notification | P0 |
| FR3.2 | Email notification via SMTP | P0 |
| FR3.3 | WhatsApp notification via Meta Cloud API | P1 |
| FR3.4 | SMS notification via Africa's Talking | P1 |
| FR3.5 | Web Push notification via Push API | P2 |
| FR3.6 | Multi-channel simultaneous delivery | P0 |
| FR3.7 | Read/delivery receipts | P1 |
| FR3.8 | Failed notification retry (3 attempts) | P0 |
| FR3.9 | Notification history log | P1 |
| FR3.10 | Per-channel opt-in/opt-out | P0 |

### FR4: Subscription & Billing
| ID | Requirement | Priority |
|----|-------------|----------|
| FR4.1 | Free plan with 20 active reminders, Telegram only | P0 |
| FR4.2 | Premium plan ($3/mo): unlimited, all channels, recurring, advanced analytics | P0 |
| FR4.3 | Business plan ($10/mo): teams, API, white label, templates | P1 |
| FR4.4 | Stripe payment integration | P0 |
| FR4.5 | PayPal payment integration | P1 |
| FR4.6 | M-Pesa STK Push (Kenya) | P1 |
| FR4.7 | Airtel Money (Africa) | P2 |
| FR4.8 | Invoice generation and history | P1 |
| FR4.9 | Subscription auto-renewal | P0 |
| FR4.10 | Plan upgrade/downgrade | P1 |
| FR4.11 | Trial period (14 days Premium) | P1 |

### FR5: Team Collaboration
| ID | Requirement | Priority |
|----|-------------|----------|
| FR5.1 | Create team workspace | P1 |
| FR5.2 | Invite members via email | P1 |
| FR5.3 | Role-based access (Owner/Admin/Member) | P1 |
| FR5.4 | Assign reminders to team members | P1 |
| FR5.5 | Track completion status per member | P1 |
| FR5.6 | Team productivity dashboard | P2 |

### FR6: Dashboard & Analytics
| ID | Requirement | Priority |
|----|-------------|----------|
| FR6.1 | Active/completed/missed/upcoming counts | P0 |
| FR6.2 | Daily/weekly/monthly reminder trend chart | P0 |
| FR6.3 | Productivity score calculation | P1 |
| FR6.4 | Category breakdown visualization | P1 |
| FR6.5 | Upcoming reminders widget | P0 |
| FR6.6 | Quick-create reminder | P0 |

### FR7: AI Features
| ID | Requirement | Priority |
|----|-------------|----------|
| FR7.1 | Natural language date/time parsing | P0 |
| FR7.2 | Smart reminder suggestions (drink water, exercise, study) | P1 |
| FR7.3 | Study schedule generation from exam date | P2 |
| FR7.4 | Auto-categorization of reminders | P2 |
| FR7.5 | Productivity pattern analysis | P2 |

### FR8: Admin Panel
| ID | Requirement | Priority |
|----|-------------|----------|
| FR8.1 | User management (view, suspend, delete) | P0 |
| FR8.2 | Subscription overview | P0 |
| FR8.3 | Payment/transaction history | P0 |
| FR8.4 | Platform-wide analytics | P1 |
| FR8.5 | Support ticket management | P1 |
| FR8.6 | Reminder job monitoring | P1 |
| FR8.7 | Monthly Revenue (MRR) tracking | P1 |

### FR9: Template Marketplace
| ID | Requirement | Priority |
|----|-------------|----------|
| FR9.1 | Create reminder template from existing reminder | P2 |
| FR9.2 | Browse public templates | P2 |
| FR9.3 | Apply template to create reminders | P2 |
| FR9.4 | Search templates by category/tags | P2 |

### FR10: API & Webhooks
| ID | Requirement | Priority |
|----|-------------|----------|
| FR10.1 | RESTful API with JWT auth | P0 |
| FR10.2 | API rate limiting | P0 |
| FR10.3 | Webhook endpoints for reminders (trigger on complete/missed) | P1 |
| FR10.4 | Stripe webhook handler | P0 |
| FR10.5 | M-Pesa webhook/callback handler | P1 |
| FR10.6 | Telegram bot webhook handler | P0 |
| FR10.7 | WhatsApp webhook handler | P1 |
| FR10.8 | Swagger/OpenAPI documentation | P0 |

---

## 5. Non-Functional Requirements

### NFR1: Performance
| ID | Requirement | Target |
|----|-------------|--------|
| NFR1.1 | API response time (p95) | <300ms |
| NFR1.2 | API response time (p99) | <500ms |
| NFR1.3 | Reminder scheduling latency | <1s from creation |
| NFR1.4 | Notification delivery latency (Telegram/Email) | <5s |
| NFR1.5 | Dashboard load time | <2s |
| NFR1.6 | Concurrent requests handled | 5,000+ |
| NFR1.7 | Database query time (p95) | <100ms |
| NFR1.8 | Page load time (p95) | <2s |

### NFR2: Reliability
| ID | Requirement | Target |
|----|-------------|--------|
| NFR2.1 | System uptime (SLA) | 99.9% |
| NFR2.2 | Reminder delivery guarantee | At least 3 retries |
| NFR2.3 | Database backup frequency | Daily |
| NFR2.4 | Disaster recovery time (RTO) | <4 hours |
| NFR2.5 | Data recovery point (RPO) | <1 hour |
| NFR2.6 | Graceful degradation on dependency failure | Implemented |

### NFR3: Security
| ID | Requirement | Status |
|----|-------------|--------|
| NFR3.1 | Password hashing (bcrypt) | Implemented |
| NFR3.2 | JWT with short-lived access tokens (30 min) | Implemented |
| NFR3.3 | Refresh tokens (7 day expiry, rotatable) | Implemented |
| NFR3.4 | HTTPS enforcement | Implemented |
| NFR3.5 | CORS configuration | Implemented |
| NFR3.6 | Rate limiting (Redis-based) | Implemented |
| NFR3.7 | SQL injection prevention (ORM) | Implemented |
| NFR3.8 | XSS protection | Implemented |
| NFR3.9 | CSRF protection | Implemented |
| NFR3.10 | Security headers (HSTS, CSP, X-Frame-Options) | Implemented |
| NFR3.11 | Secrets management (environment variables) | Implemented |
| NFR3.12 | 2FA support | Implemented |

### NFR4: Scalability
| ID | Requirement | Target |
|----|-------------|--------|
| NFR4.1 | Maximum supported users | 100,000+ |
| NFR4.2 | Daily active users supported | 25,000+ |
| NFR4.3 | Reminders processed per minute | 10,000+ |
| NFR4.4 | Horizontal scaling (stateless backend) | Implemented |
| NFR4.5 | Database connection pooling | Implemented |
| NFR4.6 | Caching layer (Redis) | Implemented |
| NFR4.7 | Async task queue (Celery) | Implemented |
| NFR4.8 | Read replicas for reporting | Configurable |

### NFR5: Maintainability
| ID | Requirement | Status |
|----|-------------|--------|
| NFR5.1 | TypeScript throughout frontend | Implemented |
| NFR5.2 | Python type hints throughout backend | Implemented |
| NFR5.3 | Automated test suite | Implemented |
| NFR5.4 | CI/CD pipeline | Implemented |
| NFR5.5 | Code linting (ruff, eslint) | Implemented |
| NFR5.6 | Database migration system (Alembic) | Implemented |
| NFR5.7 | Docker containerization | Implemented |
| NFR5.8 | Monitoring and alerting | Implemented |
| NFR5.9 | Structured logging | Implemented |

### NFR6: Accessibility
| ID | Requirement | Status |
|----|-------------|--------|
| NFR6.1 | WCAG 2.1 AA compliance | Target |
| NFR6.2 | Keyboard navigation | Implemented |
| NFR6.3 | Screen reader support (aria labels) | Implemented |
| NFR6.4 | Color contrast ratios | Implemented |

### NFR7: Localization
| ID | Requirement | Status |
|----|-------------|--------|
| NFR7.1 | English (default) | Implemented |
| NFR7.2 | Timezone-aware displays | Implemented |
| NFR7.3 | Number/currency formatting per locale | Planned |
| NFR7.4 | Right-to-left (RTL) support | Planned |

---

## 6. User Stories

### US1: First-Time User
> **As a** new visitor,  
> **I want to** sign up with my email or Google account,  
> **So that** I can create my first reminder immediately.

**Acceptance:**
- Registration with email/password or Google OAuth
- Email verification required
- Welcome tour or empty-state guidance
- Can create a reminder within 3 clicks of signup

### US2: Natural Language Creation
> **As a** busy professional,  
> **I want to** type "Remind me tomorrow at 9am to submit the report",  
> **So that** the system parses my intent without manual form filling.

**Acceptance:**
- Parser extracts time, date, message, repeat pattern
- Supports: "in X minutes/hours", "tomorrow at X", "every Monday", "next week"
- Shows parsed result for confirmation before saving
- Falls back to form if parsing fails

### US3: Multi-Channel Delivery
> **As a** user who needs redundancy,  
> **I want to** receive reminders on both Telegram and Email,  
> **So that** I never miss an important reminder even if one channel is down.

**Acceptance:**
- Can select multiple channels per reminder
- All channels fire simultaneously
- Each channel logged independently in notification history
- Failed channels retried up to 3 times

### US4: Recurring Schedule
> **As a** health-conscious user,  
> **I want to** set a reminder to "Drink water every 2 hours",  
> **So that** I maintain healthy habits automatically.

**Acceptance:**
- Repeat every N minutes/hours/days
- Daily at specific time
- Weekly on specific days
- Monthly on specific date
- Custom cron expression
- Recurring reminders stop at end date or after N occurrences

### US5: Team Management
> **As a** team lead,  
> **I want to** assign reminders to team members and track completion,  
> **So that** I can ensure deadlines are met.

**Acceptance:**
- Create team workspace
- Invite members via email
- Assign reminder to specific member
- Member gets notification about assigned reminder
- Lead can see completion status

### US6: Premium Upgrade
> **As a** free user hitting the 20-reminder limit,  
> **I want to** upgrade to Premium with M-Pesa,  
> **So that** I can create unlimited reminders.

**Acceptance:**
- Upgrade flow from dashboard
- Multiple payment methods (Stripe/PayPal/M-Pesa)
- Immediate plan activation after payment
- Pro-rated billing for mid-cycle upgrades
- Clear feature comparison before upgrade

### US7: AI Assistant
> **As a** student,  
> **I want to** say "I need to prepare for exams next month",  
> **So that** the AI generates a study schedule with daily reminders.

**Acceptance:**
- AI creates daily study reminders for each subject
- Spreads study sessions evenly across available days
- Tracks completion and adjusts schedule
- Provides productivity insights

### US8: Admin Oversight
> **As a** platform admin,  
> **I want to** view all users, subscriptions, and platform metrics,  
> **So that** I can ensure smooth operation and address issues.

**Acceptance:**
- Full user list with search/filter/sort
- Subscription breakdown by plan
- MRR and revenue charts
- Failed job monitoring and retry
- Support ticket queue

---

## 7. Feature Specifications

### 7.1 Reminder Data Model

```
Reminder {
  id: UUID (PK)
  user_id: UUID (FK -> users)
  title: string (required, max 255 chars)
  description: text (optional, max 2000 chars)
  reminder_time: datetime (required, with timezone)
  timezone: string (default: UTC)
  priority: enum [low, medium, high, urgent] (default: medium)
  category_id: UUID (FK -> categories, optional)
  notification_type: enum [telegram, whatsapp, email, sms, push, all]
  repeat_type: enum [none, daily, weekly, monthly, yearly, custom]
  repeat_interval: int (optional, for every N days/hours)
  repeat_end_date: datetime (optional)
  cron_expression: string (optional, for custom repeat)
  is_recurring: boolean
  is_active: boolean (default: true)
  is_paused: boolean (default: false)
  is_completed: boolean (default: false)
  job_id: string (scheduler reference)
  completed_at: datetime (nullable)
  created_at: datetime
  updated_at: datetime
}
```

### 7.2 Natural Language Grammar

Supported patterns:

| Pattern | Example |
|---------|---------|
| "remind me in {N} {unit}" | "remind me in 15 minutes" |
| "remind me {relative_day} at {time}" | "remind me tomorrow at 8am" |
| "remind me every {day} at {time}" | "remind me every Monday at 9am" |
| "remind me next {week/month}" | "remind me next week to pay rent" |
| "remind me on {date} at {time}" | "remind me on June 15 at 3pm" |
| "{action} every {N} {unit}" | "drink water every 2 hours" |

### 7.3 Subscription Plans

| Feature | Free | Premium ($3/mo) | Business ($10/mo) |
|---------|------|-----------------|-------------------|
| Active Reminders | 20 | Unlimited | Unlimited |
| Recurring Reminders | — | ✓ | ✓ |
| Telegram Notifications | ✓ | ✓ | ✓ |
| Email Notifications | — | ✓ | ✓ |
| WhatsApp Notifications | — | ✓ | ✓ |
| SMS Notifications | — | ✓ | ✓ |
| Push Notifications | — | ✓ | ✓ |
| Basic Analytics | ✓ | ✓ | ✓ |
| Advanced Analytics | — | ✓ | ✓ |
| Priority Queue | — | ✓ | ✓ |
| Team Members | — | — | Up to 10 |
| Shared Workspaces | — | — | ✓ |
| Reminder Templates | — | — | ✓ |
| API Access | — | — | ✓ |
| White Label | — | — | ✓ |

### 7.4 Notification Channel Specifications

| Channel | Protocol | Library | Retry | Delivery Guarantee |
|---------|----------|---------|-------|-------------------|
| Telegram | Bot API (polling/webhook) | python-telegram-bot | 3x (5min interval) | Best-effort |
| Email | SMTP (TLS) | smtplib | 3x (15min interval) | Queue-based |
| WhatsApp | Cloud API (HTTP) | requests | 3x (5min interval) | Callback webhook |
| SMS | Africa's Talking API | africastalking | 3x (10min interval) | DLR callback |
| Push | Web Push API (VAPID) | pywebpush | 2x (1min interval) | Service worker |

---

## 8. API Specifications

### 8.1 Base URL
- **Production:** `https://api.reminderbotpro.com/api/v1`
- **Staging:** `https://staging-api.reminderbotpro.com/api/v1`
- **Local:** `http://localhost:8000/api/v1`

### 8.2 Authentication
All endpoints except `/auth/*` require:
```
Authorization: Bearer <access_token>
```

### 8.3 Rate Limiting
| Tier | Requests/min |
|------|-------------|
| Free | 60 |
| Premium | 300 |
| Business | 1000 |
| Admin | 5000 |

### 8.4 Standard Response Format
```json
{
  "success": true,
  "data": {},
  "message": "Operation completed",
  "meta": {
    "page": 1,
    "limit": 20,
    "total": 100,
    "pages": 5
  }
}
```

### 8.5 Error Response Format
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": [
      { "field": "title", "message": "Title is required" }
    ]
  }
}
```

### 8.6 Endpoint Summary

| Group | Endpoints | Auth |
|-------|-----------|------|
| Auth | `/auth/register`, `/auth/login`, `/auth/refresh-token`, `/auth/verify-email`, `/auth/forgot-password`, `/auth/reset-password`, `/auth/2fa/*`, `/auth/oauth/*`, `/auth/me` | Mixed |
| Reminders | `/reminders` (CRUD), `/reminders/{id}/pause`, `/reminders/{id}/resume`, `/reminders/{id}/complete`, `/reminders/parse`, `/reminders/bulk-action`, `/reminders/upcoming` | Required |
| Categories | `/categories` (CRUD) | Required |
| Subscriptions | `/subscriptions`, `/subscriptions/plans`, `/subscriptions/cancel` | Required |
| Payments | `/payments`, `/payments/stripe`, `/payments/paypal`, `/payments/mpesa`, `/payments/airtel` | Required |
| Teams | `/teams` (CRUD), `/teams/{id}/members`, `/teams/{id}/invite`, `/teams/{id}/reminders` | Required |
| Analytics | `/analytics/stats`, `/analytics/trends`, `/analytics/productivity`, `/analytics/categories` | Required |
| Admin | `/admin/users`, `/admin/subscriptions`, `/admin/payments`, `/admin/analytics`, `/admin/tickets`, `/admin/jobs` | Admin |
| Webhooks | `/webhooks/stripe`, `/webhooks/mpesa`, `/webhooks/telegram`, `/webhooks/whatsapp` | Signature |

---

## 9. Database Requirements

### 9.1 Database System
- **Primary:** PostgreSQL 16+
- **Cache:** Redis 7+
- **Queue:** Redis (Celery broker)

### 9.2 Schema Design Principles
- UUID primary keys for all tables
- Created/updated timestamps on all tables
- Soft deletes where applicable (users, reminders)
- Proper foreign key constraints
- Composite indexes on frequent query patterns
- JSON fields for flexible metadata

### 9.3 Tables

| Table | Purpose | Key Indexes |
|-------|---------|-------------|
| `users` | User accounts | email (unique), telegram_id, google_id, github_id |
| `subscriptions` | Plan subscriptions | user_id, status, expires_at |
| `reminders` | User reminders | (user_id, is_active, reminder_time), category_id |
| `categories` | Reminder categories | user_id, name |
| `notifications` | Delivery records | reminder_id, user_id, status, channel |
| `payments` | Transaction records | user_id, provider_reference, status |
| `teams` | Team workspaces | owner_id |
| `team_members` | Team membership | (team_id, user_id) unique |
| `team_reminders` | Team-assigned reminders | team_id, assigned_to, status |
| `activity_logs` | Audit trail | user_id, action, created_at |
| `support_tickets` | Support requests | user_id, status |
| `ticket_responses` | Ticket replies | ticket_id, user_id |
| `webhook_endpoints` | User webhooks | user_id |
| `reminder_templates` | Marketplace templates | category, is_public |

### 9.4 Estimated Data Volume

| Table | 100K Users | 1 Year | Growth Rate |
|-------|-----------|--------|-------------|
| users | 100,000 | 250,000 | +20K/mo |
| reminders | 2,000,000 | 10,000,000 | +500K/mo |
| notifications | 10,000,000 | 50,000,000 | +2.5M/mo |
| payments | 50,000 | 200,000 | +10K/mo |
| activity_logs | 50,000,000 | 200,000,000 | +10M/mo |

### 9.5 Data Retention Policy
| Data | Retention | Cleanup |
|------|-----------|---------|
| Active reminders | Indefinite | — |
| Completed reminders | 90 days | Archive then delete |
| Notifications | 30 days | Delete |
| Activity logs | 90 days | Aggregate then delete |
| Soft-deleted users | 30 days | Permanent delete |
| Payment records | 7 years (legal) | Archive |

---

## 10. Security Requirements

### 10.1 Authentication & Authorization
- Passwords: bcrypt (12 rounds minimum)
- JWT: RS256 or HS256 (via python-jose)
- Access token: 30 minutes
- Refresh token: 7 days (rotatable, revocable)
- OAuth: State parameter + PKCE for mobile
- Rate limiting: 5 login attempts per minute per IP
- Account lockout: After 10 failed attempts (15 min cooldown)

### 10.2 Data Protection
- At rest: PostgreSQL encryption at disk level
- In transit: TLS 1.3 minimum
- PII: Email, phone, name encrypted at application level (AES-256)
- API keys: Hashed before storage (SHA-256)
- Webhook secrets: Unique per endpoint, stored hashed

### 10.3 API Security
- CORS: Whitelist specific origins
- Request validation: Pydantic schemas on all inputs
- SQL injection: Prevented via SQLAlchemy ORM (parameterized queries)
- XSS: Input sanitization, CSP headers
- CSRF: Double-submit cookie pattern or SameSite=Strict
- Rate limiting: Per-user, per-IP, per-endpoint

### 10.4 Infrastructure Security
- Docker: Non-root user in containers
- Secrets: Never in code, always in env vars / secrets manager
- Network: Internal services on isolated Docker network
- Database: Private subnet, no public access
- Monitoring: Audit logs for all admin actions

### 10.5 Compliance
- GDPR: Right to deletion, data export, consent records
- PCI-DSS: Payments handled by Stripe/PayPal (no raw card storage)
- SOC2: Audit logging, access controls (target)

---

## 11. Integration Requirements

### 11.1 Telegram Bot
- **Framework:** python-telegram-bot v20+
- **Mode:** Webhook (production), Polling (development)
- **Commands:**
  - `/start` — Welcome message
  - `/remind <time> <message>` — Quick reminder
  - `/myreminders` — List reminders
  - `/help` — Help text
- **Capabilities:** Inline keyboards, markdown formatting, callback queries

### 11.2 WhatsApp Cloud API
- **Provider:** Meta (official WhatsApp Business API)
- **Auth:** Permanent access token via Meta app
- **Template:** Pre-approved message templates for first outreach
- **Webhook:** Inbound message receipts, delivery status callbacks

### 11.3 Email (SMTP)
- **Provider:** SendGrid / Amazon SES / SMTP relay
- **Templates:** HTML with inline CSS, plain text fallback
- **Queue:** Retry queue for failed sends (3 attempts)
- **Tracking:** Open rate via pixel (optional), bounce handling

### 11.4 SMS (Africa's Talking)
- **Provider:** Africa's Talking
- **Coverage:** 50+ African countries
- **DLR:** Delivery receipt callbacks
- **Sender ID:** Alphanumeric (where supported), shared short code fallback

### 11.5 Push Notifications
- **Standard:** Web Push API (W3C)
- **VAPID:** Voluntary Application Server Identification
- **Service Workers:** Background notification handling
- **Browser Support:** Chrome, Firefox, Edge, Safari 16+

### 11.6 Payment Providers

#### Stripe
- **Products:** 3 pricing plans (monthly)
- **Webhook Events:** `checkout.session.completed`, `invoice.paid`, `customer.subscription.updated`
- **Metadata:** user_id, plan_type for reconciliation

#### PayPal
- **API:** PayPal REST API (v2)
- **Products:** Billing plans
- **Webhook:** `PAYMENT.SALE.COMPLETED`, `BILLING.SUBSCRIPTION.*`

#### M-Pesa (Safaricom)
- **API:** M-Pesa Daraja API v2
- **Flow:** STK Push -> Customer prompt -> Callback -> Success/Failure
- **Tabs:** Customer Paybill (business number + account reference)

#### Airtel Money
- **API:** Airtel Money API
- **Flow:** Similar STK Push model
- **Coverage:** Kenya, Tanzania, Uganda, Zambia, others

---

## 12. Performance Requirements

### 12.1 Backend Performance
| Metric | Target | Measurement |
|--------|--------|-------------|
| Request throughput | 5,000 req/s | k6 load testing |
| p50 latency | <100ms | APM (Sentry/Datadog) |
| p95 latency | <300ms | APM |
| p99 latency | <500ms | APM |
| Concurrent DB connections | 50-200 | pgBouncer pool |
| Redis operations/s | 10,000+ | Redis INFO stats |

### 12.2 Frontend Performance
| Metric | Target |
|--------|--------|
| First Contentful Paint (FCP) | <1.5s |
| Largest Contentful Paint (LCP) | <2.5s |
| First Input Delay (FID) | <100ms |
| Cumulative Layout Shift (CLS) | <0.1 |
| Time to Interactive (TTI) | <3.5s |
| Lighthouse Performance Score | >90 |

### 12.3 Notification Delivery Performance
| Channel | p50 Delivery | p95 Delivery | p99 Delivery |
|---------|-------------|-------------|-------------|
| Telegram | <1s | <3s | <10s |
| Email | <5s | <30s | <60s |
| WhatsApp | <2s | <10s | <30s |
| SMS | <10s | <30s | <60s |
| Push | <1s | <3s | <10s |

---

## 13. Scalability Requirements

### 13.1 Horizontal Scaling Architecture
- **Backend:** Stateless FastAPI behind load balancer, horizontal scale via container replicas
- **Workers:** Celery worker pool auto-scaled based on queue depth
- **Database:** PostgreSQL with read replicas for analytics, connection pooling via pgBouncer
- **Cache:** Redis cluster for distributed caching and session storage
- **CDN:** Static assets via CDN (Vercel Edge / Cloudflare)

### 13.2 Scaling Targets
| Component | Initial | 10K Users | 100K Users |
|-----------|---------|-----------|------------|
| Backend replicas | 2 | 5 | 20 |
| Celery workers | 2 | 4 | 15 |
| Celery beat | 1 | 1 | 2 (HA) |
| PostgreSQL | 1 instance | 1 + 1 replica | 2 + 2 replicas |
| Redis | 1 instance | 1 cluster node | 3 cluster nodes |
| pgBouncer | 1 instance | 2 instances | 3 instances |

### 13.3 Database Connection Pooling
- Application pool: 10-50 connections per backend instance
- pgBouncer: Transaction pooling mode, 200-500 max connections
- Statement timeout: 30s
- Idle transaction timeout: 60s

### 13.4 Caching Strategy
| Data | Cache | TTL | Invalidation |
|------|-------|-----|-------------|
| User session | Redis | 7 days | On logout |
| User profile | Redis | 5 min | On profile update |
| Reminder list | Redis | 1 min | On CRUD |
| Analytics aggregates | Redis | 1 hour | On new data |
| Subscription status | Redis | 10 min | On payment |
| Rate limit counters | Redis | Window-based | TTL expiry |
| API responses | Redis (optional) | Configurable | On related mutation |

### 13.5 Queue Depth & Worker Scaling
- Estimated queue volume: 500-5,000 reminders/min at 100K users
- Worker concurrency: 4-8 tasks per worker
- Auto-scaling: Add workers when queue depth > 1,000
- Max queue retention: 7 days
- Dead letter queue: Failed tasks after max retries

---

## 14. Compliance & Legal

### 14.1 Data Protection Compliance
- **GDPR:** Full compliance required (EU users)
- **CCPA:** Required for California users
- **POPIA:** Required for South African users
- **Data Processing Agreement (DPA):** Available on request

### 14.2 GDPR Requirements
| Requirement | Implementation |
|-------------|---------------|
| Right to access | User data export endpoint |
| Right to rectification | Profile edit functionality |
| Right to erasure | Account deletion (with 30-day soft delete) |
| Right to restrict processing | Settings to disable analytics |
| Right to data portability | JSON/CSV export |
| Consent management | Cookie consent, marketing opt-in |
| Data breach notification | Automated alerting system |
| DPA | Signed agreement available |

### 14.3 Payment Compliance
- **PCI-DSS:** Fully handled by Stripe/PayPal (SAQ A)
- No credit card data stored on our servers
- Payment logs: Masked card details only
- Refund policy: 14-day money-back guarantee

### 14.4 Terms of Service & Privacy
- Terms of Service: Governing usage, limitations, acceptable use
- Privacy Policy: Data collection, usage, sharing practices
- SLA: 99.9% uptime guarantee (Premium/Business)
- DMCA: Copyright infringement takedown process

---

## 15. Acceptance Criteria

### 15.1 Alpha Release
- [x] User registration and login (email, Google, GitHub)
- [x] Basic reminder CRUD
- [x] Telegram notification delivery
- [x] Email notification delivery
- [x] Natural language parsing for date/time
- [x] Free and Premium subscription plans
- [x] Stripe payment integration
- [x] User dashboard with basic stats
- [x] Admin user management
- [x] API documentation (Swagger)
- [x] Docker development environment
- [x] Database migrations

### 15.2 Beta Release
- [ ] WhatsApp notification delivery
- [ ] SMS notification delivery (Africa's Talking)
- [ ] Push notification delivery
- [ ] M-Pesa and PayPal payment integration
- [ ] Team collaboration features
- [ ] Recurring reminders with cron support
- [ ] Bulk reminder actions
- [ ] Advanced analytics and productivity scoring
- [ ] AI-powered reminder suggestions
- [ ] Template marketplace
- [ ] 2FA authentication
- [ ] Webhook endpoints for developers
- [ ] PWA support
- [ ] CI/CD pipeline fully operational
- [ ] Monitoring stack deployed

### 15.3 Production Release
- [ ] Load testing passed (5,000 concurrent users)
- [ ] Security audit completed
- [ ] Penetration testing passed
- [ ] GDPR compliance verified
- [ ] All payment integrations tested end-to-end
- [ ] 99.9% uptime demonstrated over 30 days
- [ ] Documentation complete (API, deployment, user guide)
- [ ] Support system operational
- [ ] Backup/restore procedures verified
- [ ] Disaster recovery drill completed

---

## 16. Glossary

| Term | Definition |
|------|------------|
| **Access Token** | Short-lived JWT used to authenticate API requests |
| **APScheduler** | Python library for scheduling lightweight jobs in-process |
| **Celery** | Distributed task queue for asynchronous job processing |
| **Cron Expression** | String syntax for specifying schedule patterns (minute/hour/day/month/weekday) |
| **CSRF** | Cross-Site Request Forgery — attack that tricks user into submitting malicious requests |
| **DLR** | Delivery Receipt — confirmation that an SMS was delivered |
| **JWT** | JSON Web Token — compact, URL-safe token format for authentication |
| **M-Pesa** | Mobile money transfer service popular in Kenya and East Africa |
| **MRR** | Monthly Recurring Revenue — predictable monthly income from subscriptions |
| **NLU** | Natural Language Understanding — parsing human language into structured data |
| **OAuth** | Open standard for token-based authentication and authorization |
| **STK Push** | M-Pesa API flow that sends a payment prompt to the customer's phone |
| **TOTP** | Time-based One-Time Password — algorithm for 2FA |
| **VAPID** | Voluntary Application Server Identification — standard for Web Push authentication |
| **Web Push** | Browser push notification standard allowing sites to send notifications |
| **Webhook** | HTTP callback that sends real-time data to a specified URL when events occur |
| **White Label** | Rebrading a product so it appears as the reseller's own |

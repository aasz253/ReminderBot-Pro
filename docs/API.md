# ReminderBot Pro - API Documentation

Base URL: `https://api.reminderbot.example.com/api/v1`

## Authentication

All API requests (except auth endpoints) require a Bearer token:

```
Authorization: Bearer <access_token>
```

### Token Flow
1. `POST /auth/login` — Get access + refresh tokens
2. `POST /auth/refresh` — Exchange refresh token for new access token
3. `POST /auth/logout` — Invalidate current tokens

### Error Responses
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Human-readable error description",
    "details": {}
  }
}
```

## Rate Limits

| Tier    | Requests/min | Burst |
|---------|-------------|-------|
| Free    | 60          | 20    |
| Pro     | 300         | 50    |
| Business| 1000        | 200   |

Rate limit headers included in every response:
- `X-RateLimit-Limit`
- `X-RateLimit-Remaining`
- `X-RateLimit-Reset`

---

## Endpoints

### Auth

#### `POST /auth/register`
Register a new user account.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecureP@ss1",
  "full_name": "John Doe"
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  "created_at": "2024-01-01T00:00:00Z"
}
```

**Errors:** `EMAIL_EXISTS`, `VALIDATION_ERROR`

#### `POST /auth/login`
Authenticate and receive tokens.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecureP@ss1"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 900
}
```

**Errors:** `INVALID_CREDENTIALS`, `ACCOUNT_LOCKED`, `ACCOUNT_NOT_VERIFIED`

#### `POST /auth/refresh`
Refresh access token.

**Request:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 900
}
```

#### `POST /auth/logout`
Invalidate current tokens. Requires authentication.

#### `GET /auth/me`
Get current user profile. Requires authentication.

**Response (200):**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  "avatar_url": "https://...",
  "is_verified": true,
  "subscription": {
    "plan": "pro",
    "status": "active",
    "renews_at": "2024-02-01T00:00:00Z"
  },
  "settings": {
    "timezone": "America/New_York",
    "default_reminder_time": "09:00",
    "notification_preferences": {
      "email": true,
      "sms": false,
      "push": true
    }
  },
  "created_at": "2024-01-01T00:00:00Z"
}
```

---

### Reminders

#### `GET /reminders`
List user's reminders. Supports pagination, filtering, and sorting.

**Query Parameters:**
| Param     | Type   | Default | Description                    |
|-----------|--------|---------|--------------------------------|
| page      | int    | 1       | Page number                    |
| per_page  | int    | 20      | Items per page (max 100)       |
| status    | str    | -       | Filter: active, completed, archived |
| priority  | str    | -       | Filter: low, medium, high, urgent |
| category  | uuid   | -       | Filter by category ID          |
| search    | str    | -       | Search in title/description    |
| sort_by   | str    | due_at  | Sort field                     |
| sort_dir  | str    | asc     | asc or desc                    |
| due_before| str    | -       | ISO 8601 datetime              |
| due_after | str    | -       | ISO 8601 datetime              |

**Response (200):**
```json
{
  "data": [
    {
      "id": "uuid",
      "title": "Team standup",
      "description": "Daily standup meeting",
      "due_at": "2024-01-15T09:00:00Z",
      "priority": "high",
      "status": "active",
      "category": {
        "id": "uuid",
        "name": "Work",
        "color": "#4A90D9"
      },
      "recurring": null,
      "notification": {
        "method": "email",
        "remind_before_minutes": 15
      },
      "completed_at": null,
      "created_at": "2024-01-10T00:00:00Z",
      "updated_at": "2024-01-10T00:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 42,
    "total_pages": 3,
    "has_next": true,
    "has_prev": false
  }
}
```

#### `POST /reminders`
Create a new reminder.

**Request:**
```json
{
  "title": "Team standup",
  "description": "Daily standup with engineering team",
  "due_at": "2024-01-15T09:00:00Z",
  "priority": "high",
  "category_id": "uuid",
  "recurring": {
    "type": "daily",
    "interval": 1,
    "ends_at": null
  },
  "notification": {
    "method": "email",
    "remind_before_minutes": 15
  }
}
```

**Response (201):** Reminder object

**Errors:** `VALIDATION_ERROR`, `CATEGORY_NOT_FOUND`, `REMINDER_LIMIT_REACHED`

#### `GET /reminders/{id}`
Get a specific reminder.

#### `PATCH /reminders/{id}`
Update a reminder (partial update).

**Request:** Any subset of reminder fields.

#### `DELETE /reminders/{id}`
Delete a reminder.

#### `POST /reminders/{id}/complete`
Mark reminder as completed.

#### `POST /reminders/{id}/snooze`
Snooze a reminder.

**Request:**
```json
{
  "until": "2024-01-15T10:00:00Z"
}
```

#### `GET /reminders/stats`
Get reminder statistics.

**Response (200):**
```json
{
  "total": 150,
  "active": 45,
  "completed_today": 12,
  "overdue": 5,
  "by_priority": {
    "low": 10,
    "medium": 20,
    "high": 12,
    "urgent": 3
  },
  "by_category": [
    {"id": "uuid", "name": "Work", "count": 20}
  ]
}
```

---

### Categories

#### `GET /categories`
List categories.

#### `POST /categories`
Create a category.

**Request:**
```json
{
  "name": "Work",
  "description": "Work-related reminders",
  "color": "#4A90D9"
}
```

#### `PATCH /categories/{id}`
Update a category.

#### `DELETE /categories/{id}`
Delete a category (reminders become uncategorized).

---

### Subscriptions

#### `GET /subscriptions/plans`
List available subscription plans.

**Response (200):**
```json
{
  "data": [
    {
      "id": "uuid",
      "name": "Free",
      "price": 0,
      "interval": "month",
      "features": {
        "max_reminders": 10,
        "sms_enabled": false,
        "team_members": 1
      }
    },
    {
      "id": "uuid",
      "name": "Pro",
      "price": 9.99,
      "interval": "month",
      "features": {
        "max_reminders": 1000,
        "sms_enabled": true,
        "team_members": 10
      }
    }
  ]
}
```

#### `POST /subscriptions/create`
Create a subscription checkout session.

**Request:**
```json
{
  "plan_id": "uuid",
  "success_url": "https://reminderbot.example.com/settings/billing?success=true",
  "cancel_url": "https://reminderbot.example.com/settings/billing?canceled=true"
}
```

**Response (200):**
```json
{
  "checkout_url": "https://checkout.stripe.com/pay/cs_..."
}
```

#### `POST /subscriptions/cancel`
Cancel current subscription.

#### `GET /subscriptions/invoices`
List invoices.

**Query Parameters:** `page`, `per_page`

---

### Webhooks

Stripe webhooks are sent to `POST /webhooks/stripe`.

**Events handled:**
| Event                          | Action                          |
|--------------------------------|---------------------------------|
| `checkout.session.completed`   | Activate subscription           |
| `invoice.paid`                 | Renew subscription              |
| `invoice.payment_failed`       | Send payment failure notice     |
| `customer.subscription.deleted`| Downgrade to free               |
| `customer.subscription.updated`| Update plan details             |

---

## Error Codes

| Code                    | HTTP Status | Description                        |
|-------------------------|-------------|------------------------------------|
| `VALIDATION_ERROR`      | 422         | Request validation failed          |
| `INVALID_CREDENTIALS`   | 401         | Email or password incorrect        |
| `TOKEN_EXPIRED`         | 401         | Access token has expired           |
| `TOKEN_INVALID`         | 401         | Token is malformed or revoked      |
| `ACCOUNT_LOCKED`        | 423         | Account temporarily locked         |
| `NOT_FOUND`             | 404         | Resource not found                 |
| `FORBIDDEN`             | 403         | Insufficient permissions           |
| `RATE_LIMIT_EXCEEDED`   | 429         | Too many requests                  |
| `REMINDER_LIMIT_REACHED`| 403         | Plan limit reached                 |
| `CATEGORY_NOT_FOUND`    | 404         | Category does not exist            |
| `DUPLICATE_ENTRY`       | 409         | Resource already exists            |
| `INTERNAL_ERROR`        | 500         | Unexpected server error            |

## Pagination

All list endpoints return paginated results:

```json
{
  "data": [],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 100,
    "total_pages": 5,
    "has_next": true,
    "has_prev": false
  }
}
```

## Webhook Events (Outgoing)

Event notifications sent to registered webhook URLs:

| Event                         | Description                    |
|-------------------------------|--------------------------------|
| `reminder.created`            | New reminder created           |
| `reminder.updated`            | Reminder updated               |
| `reminder.completed`          | Reminder marked complete       |
| `reminder.overdue`            | Reminder past due              |
| `user.subscription_changed`   | Plan changed                   |
| `user.registered`             | New user registered            |

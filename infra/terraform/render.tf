terraform {
  required_providers {
    render = {
      source  = "render-oss/render"
      version = "~> 1.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.5"
    }
  }
}

provider "render" {
  api_key = var.render_api_key
}

locals {
  project_name = "reminderbot-pro"
  environment  = var.environment
}

# Web Service: Backend (FastAPI)
resource "render_web_service" "backend" {
  name            = "${local.project_name}-backend"
  plan            = var.backend_plan
  region          = var.render_region
  runtime_source  = "image"
  image_url       = "ghcr.io/${var.github_username}/reminderbot-backend:${var.image_tag}"
  health_check_path = "/api/v1/health"
  pull_request_previews_enabled = false

  disk {
    name    = "static"
    mount_path = "/static"
    size_gb = 1
  }

  environment_variables = {
    ENVIRONMENT  = local.environment
    LOG_LEVEL    = "info"
    FRONTEND_URL = "https://${var.domain_name}"
    CORS_ORIGINS = "https://${var.domain_name}"
    SMTP_HOST    = var.smtp_host
    SMTP_PORT    = var.smtp_port
    SMTP_USER    = var.smtp_user
  }

  secret_files = [
    {
      name     = "env-secrets"
      contents = base64encode(jsonencode({
        DATABASE_URL          = var.database_url
        REDIS_URL             = var.redis_url
        CELERY_BROKER_URL     = "${var.redis_url}/1"
        CELERY_RESULT_BACKEND = "${var.redis_url}/2"
        SECRET_KEY            = random_password.secret_key.result
        SMTP_PASSWORD         = var.smtp_password
        SENTRY_DSN            = var.sentry_dsn
        STRIPE_SECRET_KEY     = var.stripe_secret_key
        STRIPE_WEBHOOK_SECRET = var.stripe_webhook_secret
      }))
    }
  ]
}

# Background Worker: Celery
resource "render_cron_job" "celery_worker" {
  name           = "${local.project_name}-celery-worker"
  plan           = var.worker_plan
  region         = var.render_region
  schedule       = "* * * * *"  # Runs every minute (Celery worker)
  runtime_source = "image"
  image_url      = "ghcr.io/${var.github_username}/reminderbot-backend:${var.image_tag}"

  start_command = "celery -A app.core.celery_app worker --loglevel=info --concurrency=2"

  environment_variables = {
    ENVIRONMENT = local.environment
    LOG_LEVEL   = "info"
  }

  secret_files = [
    {
      name     = "env-secrets"
      contents = base64encode(jsonencode({
        DATABASE_URL          = var.database_url
        REDIS_URL             = var.redis_url
        CELERY_BROKER_URL     = "${var.redis_url}/1"
        CELERY_RESULT_BACKEND = "${var.redis_url}/2"
        SECRET_KEY            = random_password.secret_key.result
        SMTP_PASSWORD         = var.smtp_password
        SENTRY_DSN            = var.sentry_dsn
      }))
    }
  ]
}

# Cron Job: Celery Beat
resource "render_cron_job" "celery_beat" {
  name           = "${local.project_name}-celery-beat"
  plan           = "free"
  region         = var.render_region
  schedule       = "* * * * *"
  runtime_source = "image"
  image_url      = "ghcr.io/${var.github_username}/reminderbot-backend:${var.image_tag}"

  start_command = "celery -A app.core.celery_app beat --loglevel=info"

  environment_variables = {
    ENVIRONMENT = local.environment
    LOG_LEVEL   = "info"
  }

  secret_files = [
    {
      name     = "env-secrets"
      contents = base64encode(jsonencode({
        DATABASE_URL          = var.database_url
        REDIS_URL             = var.redis_url
        CELERY_BROKER_URL     = "${var.redis_url}/1"
        CELERY_RESULT_BACKEND = "${var.redis_url}/2"
        SECRET_KEY            = random_password.secret_key.result
      }))
    }
  ]
}

# Static Site: Frontend (Next.js)
resource "render_web_service" "frontend" {
  name   = "${local.project_name}-frontend"
  plan   = var.frontend_plan
  region = var.render_region
  runtime_source = "image"
  image_url      = "ghcr.io/${var.github_username}/reminderbot-frontend:${var.image_tag}"

  health_check_path = "/"
  pull_request_previews_enabled = false

  environment_variables = {
    NEXT_PUBLIC_API_URL = "https://api.${var.domain_name}"
    NEXT_PUBLIC_WS_URL  = "wss://api.${var.domain_name}/ws"
  }
}

# Custom Domain
resource "render_custom_domain" "app" {
  service_id = render_web_service.frontend.id
  domain     = var.domain_name
}

resource "render_custom_domain" "api" {
  service_id = render_web_service.backend.id
  domain     = "api.${var.domain_name}"
}

# PostgreSQL (Render Managed)
resource "render_postgres" "main" {
  name   = "${local.project_name}-postgres"
  plan   = var.postgres_plan
  region = var.render_region
  version = "16"

  disk_size_gb = var.postgres_disk_size
}

# Redis (Render Managed)
resource "render_redis" "main" {
  name   = "${local.project_name}-redis"
  plan   = var.redis_plan
  region = var.render_region

  maxmemory_policy = "allkeys-lru"
}

resource "random_password" "secret_key" {
  length  = 64
  special = false
}

output "backend_url" {
  value = "https://api.${var.domain_name}"
}

output "frontend_url" {
  value = "https://${var.domain_name}"
}

output "database_url" {
  value     = render_postgres.main.connection_string
  sensitive = true
}

output "redis_url" {
  value     = render_redis.main.connection_string
  sensitive = true
}

terraform {
  required_providers {
    railway = {
      source  = "wayfair/railway"
      version = "~> 1.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.5"
    }
  }
}

provider "railway" {
  token = var.railway_token
}

locals {
  project_name = "reminderbot-pro"
  environment  = var.environment
}

resource "railway_project" "main" {
  name        = local.project_name
  description = "ReminderBot Pro - Smart Reminder Management"
}

resource "railway_environment" "production" {
  project_id = railway_project.main.id
  name       = "production"
}

# PostgreSQL
resource "railway_plugin" "postgres" {
  project_id = railway_project.main.id
  plugin     = "postgresql"
  provider   = "aws"
  region     = "us-east-1"
}

# Redis
resource "railway_plugin" "redis" {
  project_id = railway_project.main.id
  plugin     = "redis"
  provider   = "aws"
  region     = "us-east-1"
}

# Backend Service
resource "railway_service" "backend" {
  project_id = railway_project.main.id
  name       = "backend"
  source {
    image = "ghcr.io/${var.github_username}/reminderbot-backend:${var.image_tag}"
  }
  domain = "api.${var.domain_name}"
}

resource "railway_service_instance" "backend" {
  project_id     = railway_project.main.id
  service_id     = railway_service.backend.id
  environment_id = railway_environment.production.id

  port = 8000

  replicas = var.backend_replicas

  resources {
    cpu    = var.backend_cpu
    memory = var.backend_memory
  }

  healthcheck {
    path     = "/api/v1/health"
    interval = 30
    timeout  = 10
    retries  = 3
  }

  environment_variables = {
    DATABASE_URL        = railway_plugin.postgres.connection_uri
    REDIS_URL           = railway_plugin.redis.connection_uri
    CELERY_BROKER_URL   = "${railway_plugin.redis.connection_uri}/1"
    CELERY_RESULT_BACKEND = "${railway_plugin.redis.connection_uri}/2"
    SECRET_KEY          = random_password.secret_key.result
    ENVIRONMENT         = "production"
    LOG_LEVEL           = "info"
    FRONTEND_URL        = "https://${var.domain_name}"
    CORS_ORIGINS        = "https://${var.domain_name}"
    SMTP_HOST           = var.smtp_host
    SMTP_PORT           = var.smtp_port
    SMTP_USER           = var.smtp_user
    SMTP_PASSWORD       = var.smtp_password
    SENTRY_DSN          = var.sentry_dsn
    STRIPE_SECRET_KEY   = var.stripe_secret_key
    STRIPE_WEBHOOK_SECRET = var.stripe_webhook_secret
  }
}

# Celery Worker Service
resource "railway_service" "celery_worker" {
  project_id = railway_project.main.id
  name       = "celery-worker"
  source {
    image = "ghcr.io/${var.github_username}/reminderbot-backend:${var.image_tag}"
  }
}

resource "railway_service_instance" "celery_worker" {
  project_id     = railway_project.main.id
  service_id     = railway_service.celery_worker.id
  environment_id = railway_environment.production.id

  command = "celery -A app.core.celery_app worker --loglevel=info --concurrency=4"

  replicas = var.worker_replicas

  resources {
    cpu    = var.worker_cpu
    memory = var.worker_memory
  }

  environment_variables = {
    DATABASE_URL        = railway_plugin.postgres.connection_uri
    REDIS_URL           = railway_plugin.redis.connection_uri
    CELERY_BROKER_URL   = "${railway_plugin.redis.connection_uri}/1"
    CELERY_RESULT_BACKEND = "${railway_plugin.redis.connection_uri}/2"
    SECRET_KEY          = random_password.secret_key.result
    ENVIRONMENT         = "production"
    LOG_LEVEL           = "info"
    SMTP_HOST           = var.smtp_host
    SMTP_PORT           = var.smtp_port
    SMTP_USER           = var.smtp_user
    SMTP_PASSWORD       = var.smtp_password
  }
}

# Celery Beat Service
resource "railway_service" "celery_beat" {
  project_id = railway_project.main.id
  name       = "celery-beat"
  source {
    image = "ghcr.io/${var.github_username}/reminderbot-backend:${var.image_tag}"
  }
}

resource "railway_service_instance" "celery_beat" {
  project_id     = railway_project.main.id
  service_id     = railway_service.celery_beat.id
  environment_id = railway_environment.production.id

  command = "celery -A app.core.celery_app beat --loglevel=info"

  resources {
    cpu    = 0.5
    memory = 512
  }

  environment_variables = {
    DATABASE_URL        = railway_plugin.postgres.connection_uri
    REDIS_URL           = railway_plugin.redis.connection_uri
    CELERY_BROKER_URL   = "${railway_plugin.redis.connection_uri}/1"
    CELERY_RESULT_BACKEND = "${railway_plugin.redis.connection_uri}/2"
    SECRET_KEY          = random_password.secret_key.result
    ENVIRONMENT         = "production"
    LOG_LEVEL           = "info"
  }
}

# Frontend Service
resource "railway_service" "frontend" {
  project_id = railway_project.main.id
  name       = "frontend"
  source {
    image = "ghcr.io/${var.github_username}/reminderbot-frontend:${var.image_tag}"
  }
  domain = var.domain_name
}

resource "railway_service_instance" "frontend" {
  project_id     = railway_project.main.id
  service_id     = railway_service.frontend.id
  environment_id = railway_environment.production.id

  port = 3000

  replicas = var.frontend_replicas

  resources {
    cpu    = var.frontend_cpu
    memory = var.frontend_memory
  }

  environment_variables = {
    NEXT_PUBLIC_API_URL = "https://api.${var.domain_name}"
    NEXT_PUBLIC_WS_URL  = "wss://api.${var.domain_name}/ws"
  }
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

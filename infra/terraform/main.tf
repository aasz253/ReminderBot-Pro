terraform {
  required_version = ">= 1.5.0"

  required_providers {
    digitalocean = {
      source  = "digitalocean/digitalocean"
      version = "~> 2.30"
    }
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.25"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.5"
    }
  }

  backend "s3" {
    bucket = "reminderbot-terraform-state"
    key    = "production/terraform.tfstate"
    region = "us-east-1"
    encrypt = true
  }
}

provider "digitalocean" {
  token = var.do_token
}

provider "aws" {
  region = var.aws_region
  profile = var.aws_profile
}

locals {
  project_name = "reminderbot"
  environment  = var.environment
  common_tags = {
    Project     = "ReminderBotPro"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# VPC / Network
resource "digitalocean_vpc" "main" {
  name   = "${local.project_name}-${local.environment}-vpc"
  region = var.do_region
  ip_range = var.vpc_cidr
}

resource "digitalocean_droplet" "bastion" {
  count    = var.create_bastion ? 1 : 0
  name     = "${local.project_name}-bastion-${count.index + 1}"
  size     = "s-1vcpu-2gb"
  image    = "ubuntu-22-04-x64"
  region   = var.do_region
  vpc_uuid = digitalocean_vpc.main.id
  ssh_keys = [var.do_ssh_key_id]

  tags = ["bastion", local.environment]

  connection {
    type = "ssh"
    user = "root"
    host = self.ipv4_address
  }

  provisioner "remote-exec" {
    inline = [
      "apt-get update",
      "apt-get install -y postgresql-client redis-tools docker.io docker-compose-v2",
      "systemctl enable docker",
      "systemctl start docker",
    ]
  }
}

# PostgreSQL (DigitalOcean Managed Database)
resource "digitalocean_database_cluster" "postgres" {
  name       = "${local.project_name}-${local.environment}-pg"
  engine     = "pg"
  version    = "16"
  size       = var.postgres_size
  region     = var.do_region
  node_count = var.postgres_node_count
  vpc_uuid   = digitalocean_vpc.main.id

  tags = ["postgres", local.environment]
}

resource "digitalocean_database_db" "main" {
  cluster_id = digitalocean_database_cluster.postgres.id
  name       = "reminderbot"
}

resource "digitalocean_database_user" "app" {
  cluster_id = digitalocean_database_cluster.postgres.id
  name       = "reminderbot_app"
}

resource "digitalocean_database_firewall" "postgres" {
  cluster_id = digitalocean_database_cluster.postgres.id

  rule {
    type  = "droplet"
    value = digitalocean_droplet.bastion[0].id
  }

  rule {
    type  = "k8s"
    value = digitalocean_kubernetes_cluster.main.id
  }
}

# Redis (DigitalOcean Managed Database)
resource "digitalocean_database_cluster" "redis" {
  name       = "${local.project_name}-${local.environment}-redis"
  engine     = "redis"
  version    = "7"
  size       = var.redis_size
  region     = var.do_region
  node_count = var.redis_node_count
  vpc_uuid   = digitalocean_vpc.main.id

  tags = ["redis", local.environment]
}

# Kubernetes Cluster (DOKS)
resource "digitalocean_kubernetes_cluster" "main" {
  name    = "${local.project_name}-${local.environment}-k8s"
  region  = var.do_region
  version = "1.28.2-do.0"
  vpc_uuid = digitalocean_vpc.main.id

  node_pool {
    name       = "worker-pool"
    size       = var.k8s_node_size
    node_count = var.k8s_node_count
    tags       = ["worker", local.environment]

    auto_scale = true
    min_nodes  = var.k8s_min_nodes
    max_nodes  = var.k8s_max_nodes
  }
}

# Container Registry (DO CR)
resource "digitalocean_container_registry" "main" {
  name                   = "${local.project_name}-${local.environment}"
  subscription_tier_slug = var.cr_subscription_tier
  region                 = var.do_region
}

# Load Balancer
resource "digitalocean_loadbalancer" "main" {
  name     = "${local.project_name}-${local.environment}-lb"
  region   = var.do_region
  vpc_uuid = digitalocean_vpc.main.id
  type     = "regional"

  forwarding_rule {
    entry_port     = 443
    entry_protocol = "https"

    target_port     = 443
    target_protocol = "https"

    certificate_name = digitalocean_certificate.main.name
  }

  forwarding_rule {
    entry_port     = 80
    entry_protocol = "http"

    target_port     = 80
    target_protocol = "http"
  }

  healthcheck {
    port     = 80
    protocol = "http"
    path     = "/api/v1/health"
  }

  droplet_ids = digitalocean_kubernetes_cluster.main.node_pool[0].nodes[*].droplet_id
}

# SSL Certificate
resource "digitalocean_certificate" "main" {
  name    = "${local.project_name}-${local.environment}-cert"
  type    = "lets_encrypt"
  domains = [
    var.domain_name,
    "api.${var.domain_name}"
  ]
}

# DNS Records
resource "digitalocean_record" "app" {
  domain = var.domain_name
  type   = "A"
  name   = "@"
  value  = digitalocean_loadbalancer.main.ip
  ttl    = 300
}

resource "digitalocean_record" "api" {
  domain = var.domain_name
  type   = "A"
  name   = "api"
  value  = digitalocean_loadbalancer.main.ip
  ttl    = 300
}

resource "digitalocean_record" "www" {
  domain = var.domain_name
  type   = "CNAME"
  name   = "www"
  value  = "${var.domain_name}."
  ttl    = 300
}

# Random password for app secrets
resource "random_password" "secret_key" {
  length  = 64
  special = false
}

resource "random_password" "postgres_password" {
  length  = 32
  special = false
}

# Output secrets (store securely)
resource "local_file" "production_env" {
  content = templatefile("${path.module}/templates/env.tpl", {
    database_url     = "postgresql+asyncpg://${digitalocean_database_user.app.name}:${digitalocean_database_user.app.password}@${digitalocean_database_cluster.postgres.host}:${digitalocean_database_cluster.postgres.port}/reminderbot"
    redis_url        = "redis://:${digitalocean_database_cluster.redis.password}@${digitalocean_database_cluster.redis.host}:${digitalocean_database_cluster.redis.port}/0"
    secret_key       = random_password.secret_key.result
    environment      = var.environment
    domain_name      = var.domain_name
  })
  filename = "${path.module}/.env.production"
}

# Kubernetes config map for app secrets (via helm or kubectl)
resource "null_resource" "k8s_secrets" {
  depends_on = [digitalocean_kubernetes_cluster.main]

  provisioner "local-exec" {
    command = <<-EOT
      doctl kubernetes cluster kubeconfig save ${digitalocean_kubernetes_cluster.main.id}
      kubectl create namespace ${local.environment} --dry-run=client -o yaml | kubectl apply -f -
      kubectl delete secret app-secrets -n ${local.environment} 2>/dev/null || true
      kubectl create secret generic app-secrets -n ${local.environment} \
        --from-literal=DATABASE_URL="postgresql+asyncpg://${digitalocean_database_user.app.name}:${digitalocean_database_user.app.password}@${digitalocean_database_cluster.postgres.host}:${digitalocean_database_cluster.postgres.port}/reminderbot" \
        --from-literal=REDIS_URL="redis://:${digitalocean_database_cluster.redis.password}@${digitalocean_database_cluster.redis.host}:${digitalocean_database_cluster.redis.port}/0" \
        --from-literal=SECRET_KEY="${random_password.secret_key.result}"
    EOT
  }
}

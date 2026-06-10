variable "do_token" {
  description = "DigitalOcean API token"
  type        = string
  sensitive   = true
}

variable "aws_region" {
  description = "AWS region for Terraform state backend"
  type        = string
  default     = "us-east-1"
}

variable "aws_profile" {
  description = "AWS profile for Terraform state backend"
  type        = string
  default     = "default"
}

variable "environment" {
  description = "Deployment environment (production, staging, development)"
  type        = string
  default     = "production"
}

variable "do_region" {
  description = "DigitalOcean region"
  type        = string
  default     = "nyc1"
}

variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
  default     = "10.10.0.0/16"
}

variable "domain_name" {
  description = "Domain name for the application"
  type        = string
}

variable "do_ssh_key_id" {
  description = "DigitalOcean SSH key ID for bastion access"
  type        = string
  default     = ""
}

variable "create_bastion" {
  description = "Create a bastion host"
  type        = bool
  default     = true
}

variable "postgres_size" {
  description = "PostgreSQL database node size"
  type        = string
  default     = "db-s-2vcpu-4gb"
}

variable "postgres_node_count" {
  description = "Number of PostgreSQL nodes"
  type        = number
  default     = 1
}

variable "redis_size" {
  description = "Redis database node size"
  type        = string
  default     = "db-s-1vcpu-2gb"
}

variable "redis_node_count" {
  description = "Number of Redis nodes"
  type        = number
  default     = 1
}

variable "k8s_node_size" {
  description = "Kubernetes node size"
  type        = string
  default     = "s-2vcpu-4gb"
}

variable "k8s_node_count" {
  description = "Initial number of Kubernetes nodes"
  type        = number
  default     = 2
}

variable "k8s_min_nodes" {
  description = "Minimum number of Kubernetes nodes (autoscaling)"
  type        = number
  default     = 2
}

variable "k8s_max_nodes" {
  description = "Maximum number of Kubernetes nodes (autoscaling)"
  type        = number
  default     = 10
}

variable "cr_subscription_tier" {
  description = "Container Registry subscription tier"
  type        = string
  default     = "starter"
}

variable "sentry_dsn" {
  description = "Sentry DSN for error tracking"
  type        = string
  default     = ""
}

variable "slack_webhook_url" {
  description = "Slack webhook URL for deployment notifications"
  type        = string
  default     = ""
}

variable "telegram_bot_token" {
  description = "Telegram bot token for notifications"
  type        = string
  default     = ""
}

variable "telegram_chat_id" {
  description = "Telegram chat ID for notifications"
  type        = string
  default     = ""
}

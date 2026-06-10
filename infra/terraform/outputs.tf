output "vpc_id" {
  description = "ID of the created VPC"
  value       = digitalocean_vpc.main.id
}

output "postgres_host" {
  description = "PostgreSQL database host"
  value       = digitalocean_database_cluster.postgres.host
  sensitive   = true
}

output "postgres_port" {
  description = "PostgreSQL database port"
  value       = digitalocean_database_cluster.postgres.port
}

output "redis_host" {
  description = "Redis host"
  value       = digitalocean_database_cluster.redis.host
  sensitive   = true
}

output "redis_port" {
  description = "Redis port"
  value       = digitalocean_database_cluster.redis.port
}

output "kubernetes_cluster_id" {
  description = "ID of the Kubernetes cluster"
  value       = digitalocean_kubernetes_cluster.main.id
}

output "kubernetes_cluster_endpoint" {
  description = "Kubernetes cluster API endpoint"
  value       = digitalocean_kubernetes_cluster.main.endpoint
}

output "load_balancer_ip" {
  description = "Load balancer public IP"
  value       = digitalocean_loadbalancer.main.ip
}

output "domain" {
  description = "Application domain"
  value       = var.domain_name
}

output "container_registry" {
  description = "Container registry endpoint"
  value       = digitalocean_container_registry.main.server_url
}

output "bastion_ip" {
  description = "Bastion host public IP"
  value       = try(digitalocean_droplet.bastion[0].ipv4_address, null)
}

output "database_url" {
  description = "PostgreSQL connection string (for migrations)"
  value       = "postgresql+asyncpg://${digitalocean_database_user.app.name}@${digitalocean_database_cluster.postgres.host}:${digitalocean_database_cluster.postgres.port}/reminderbot"
  sensitive   = true
}

output "redis_url" {
  description = "Redis connection string"
  value       = "redis://@${digitalocean_database_cluster.redis.host}:${digitalocean_database_cluster.redis.port}/0"
  sensitive   = true
}

output "app_secret_key" {
  description = "Application secret key"
  value       = random_password.secret_key.result
  sensitive   = true
}

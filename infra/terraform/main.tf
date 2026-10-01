
# DOCUMENTATION-GRADE ONLY — not applied. Production equivalent of the local simulation.
terraform { required_providers { aws = { source = "hashicorp/aws", version = "~> 5.0" } } }
variable "region" { default = "us-east-1" }
# RDS PostgreSQL (replaces local SQLite stand-in)
resource "aws_db_instance" "policy" { engine = "postgres", instance_class = "db.t3.medium", allocated_storage = 20 }
# ECS Fargate service + CodeDeploy blue/green deployment controller, ALB with blue/green target groups,
# CloudWatch alarms (5xx error rate, p95 latency) wired to CodeDeploy automatic rollback,
# AWS Fault Injection Service experiment templates for task termination / latency injection.
# Full resource bodies omitted intentionally: this file documents the production design, it is never applied in CI for this repo.

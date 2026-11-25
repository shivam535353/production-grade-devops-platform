variable "aws_region" {
  description = "AWS region for CI infrastructure"
  type        = string
  default     = "ap-south-1"
}

variable "github_repository" {
  description = "GitHub repository in owner/repository format"
  type        = string
  default     = "shivam535353/production-grade-devops-platform"
}

variable "ecr_repository_name" {
  description = "Persistent ECR repository name"
  type        = string
  default     = "production-grade-devops-platform"
}

variable "create_github_oidc_provider" {
  description = "Create GitHub Actions OIDC provider when it does not already exist"
  type        = bool
  default     = true
}

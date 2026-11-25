output "github_actions_role_arn" {
  description = "IAM role ARN for GitHub Actions OIDC authentication"
  value       = aws_iam_role.github_actions_ecr_push.arn
}

output "ecr_repository_url" {
  description = "Persistent ECR repository URL"
  value       = aws_ecr_repository.app.repository_url
}

output "ecr_registry" {
  description = "ECR registry hostname"
  value       = split("/", aws_ecr_repository.app.repository_url)[0]
}

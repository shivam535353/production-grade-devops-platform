output "vpc_id" {
  description = "ID of the EKS demo VPC"
  value       = module.vpc.vpc_id
}

output "private_subnet_ids" {
  description = "Private subnet IDs for EKS worker nodes"
  value       = module.vpc.private_subnets
}

output "public_subnet_ids" {
  description = "Public subnet IDs for internet-facing load balancers"
  value       = module.vpc.public_subnets
}

output "azs" {
  description = "Availability Zones used by the VPC"
  value       = local.azs
}

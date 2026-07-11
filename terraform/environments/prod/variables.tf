variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "ap-south-1"    # Mumbai — India closest
}

variable "project_name" {
  description = "Project name — used in all resource names"
  type        = string
  default     = "devops-platform"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "Availability zones"
  type        = list(string)
  default     = ["ap-south-1a", "ap-south-1b"]
}

variable "public_subnets" {
  description = "Public subnet CIDRs (ALB sathi)"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_subnets" {
  description = "Private subnet CIDRs (EKS nodes sathi)"
  type        = list(string)
  default     = ["10.0.10.0/24", "10.0.11.0/24"]
}

variable "cluster_version" {
  description = "EKS Kubernetes version"
  type        = string
  default     = "1.29"
}

variable "node_groups" {
  description = "EKS node group configuration"
  type = map(object({
    instance_types = list(string)
    min_size       = number
    max_size       = number
    desired_size   = number
  }))
  default = {
    main = {
      instance_types = ["t3.medium"]    # 2 vCPU, 4GB RAM — demo sufficient
      min_size       = 1
      max_size       = 3
      desired_size   = 2
    }
  }
}
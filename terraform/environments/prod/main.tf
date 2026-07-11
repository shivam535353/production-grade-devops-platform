# =============================================================================
# production-grade-devops-platform — AWS EKS Infrastructure
# Run: terraform init → terraform plan → terraform apply
# IMPORTANT: terraform destroy after demo (cost avoid karanya sathi)
# =============================================================================

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
  }
  # Backend — S3 madhe state store (production standard)
  # backend "s3" {
  #   bucket = "your-terraform-state-bucket"
  #   key    = "production-grade-devops-platform/terraform.tfstate"
  #   region = "ap-south-1"
  # }
}

provider "aws" {
  region = var.aws_region
}

# ---------------------------------------------------------------------------
# VPC Module
# ---------------------------------------------------------------------------
module "vpc" {
  source = "../modules/vpc"

  project_name       = var.project_name
  vpc_cidr           = var.vpc_cidr
  availability_zones = var.availability_zones
  public_subnets     = var.public_subnets
  private_subnets    = var.private_subnets
  environment        = var.environment
}

# ---------------------------------------------------------------------------
# EKS Module
# ---------------------------------------------------------------------------
module "eks" {
  source = "../modules/eks"

  project_name    = var.project_name
  environment     = var.environment
  cluster_version = var.cluster_version
  vpc_id          = module.vpc.vpc_id
  private_subnets = module.vpc.private_subnet_ids
  node_groups     = var.node_groups
}
variable "region" {
  description = "AWS region"
  type        = string
  default     = "ap-south-1"
}

variable "cluster_name" {
  description = "EKS cluster name used in subnet tags"
  type        = string
  default     = "pgdp-eks-demo"
}

variable "vpc_cidr" {
  description = "CIDR block of the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "az_count" {
  description = "Number of Availability Zones"
  type        = number
  default     = 2

  validation {
    condition     = var.az_count == 2
    error_message = "This demo network is designed for exactly 2 Availability Zones."
  }
}

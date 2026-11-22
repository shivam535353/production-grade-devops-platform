terraform {
  backend "s3" {
    bucket       = "tfstate-822417885434-ap-south-1"
    key          = "eks-demo/terraform.tfstate"
    region       = "ap-south-1"
    encrypt      = true
    use_lockfile = true
  }
}

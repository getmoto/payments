terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16"
    }
  }

  required_version = ">= 1.2.0"

  backend "s3" {
    bucket         = "moto-payments-terraform-state"
    key            = "terraform.tfstate"
    region         = "us-east-1"
    profile        = "moto"
  }
}

module "infrastructure" {
  source = "./terraform"
}

output "domain-name" {
  value = module.infrastructure.domain_name
}
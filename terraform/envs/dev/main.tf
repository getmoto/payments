terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16"
    }
  }

  required_version = ">= 1.2.0"

  backend "s3" {
    bucket         = "test-moto-payments-terraform-state"
    key            = "terraform.tfstate"
    region         = "us-east-1"
  }
}

module "infrastructure" {
  source = "../../modules/infra"
  root_domain = "getmoto.org"
  domain = "test.payments.getmoto.org"
  resource_prefix = "test-"
  providers = {
    aws.useast1 = aws.useast1
  }
}

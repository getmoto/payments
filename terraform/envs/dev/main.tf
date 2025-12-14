terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
      #configuration_aliases = [ aws.useast1 ]
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
  repo_owner_name = "getmoto/testrepo"
  cloudfront_ttl = 60  # one minute
  providers = {
    aws.useast1 = aws.useast1
  }
}

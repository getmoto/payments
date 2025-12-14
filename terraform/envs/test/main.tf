terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }

  required_version = ">= 1.2.0"
}

module "infrastructure" {
  source = "../../modules/infra"
  root_domain = "getmoto.org"
  domain = "test.payments.getmoto.org"
  resource_prefix = "test-"
  cloudfront_ttl = 1  # one second
  repo_owner_name = "getmoto/testrepo"
  providers = {
    aws = aws.useast1
    aws.useast1 = aws.useast1
  }
}

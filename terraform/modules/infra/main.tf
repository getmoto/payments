terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16"
      configuration_aliases = [ aws.useast1 ]
    }
  }

  required_version = ">= 1.2.0"
}
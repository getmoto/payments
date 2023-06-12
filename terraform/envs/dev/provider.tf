provider "aws" {
  region  = "eu-west-1"
  alias = "euwest"
}

provider "aws" {
  region = "us-east-1"
  alias = "useast1"
}

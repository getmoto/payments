provider "aws" {
  region  = "eu-west-1"
}

provider "aws" {
  region = "us-east-1"
  alias = "useast1"
}

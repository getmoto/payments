provider "aws" {
  region  = "eu-west-1"
  profile = "moto"
  alias = "euwest"
}

provider "aws" {
  region = "us-east-1"
  profile = "moto"
  alias = "useast1"
}

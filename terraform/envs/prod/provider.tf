provider "aws" {
  region  = "us-east-1"
  profile = "moto"
}

provider "aws" {
  region  = "us-east-1"
  profile = "moto"
  alias = "useast1"
}
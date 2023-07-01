provider "aws" {
  region  = "us-east-1"
  alias = "useast1"

  access_key                  = "mock_access_key"
  secret_key                  = "mock_secret_key"
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true
  s3_use_path_style           = true

  endpoints {
      acm              = "http://localhost:5000"
      apigateway       = "http://localhost:5000"
      apigatewayv2     = "http://localhost:5000"
      cloudfront       = "http://localhost:5000"
      cloudwatch       = "http://localhost:5000"
      dynamodb         = "http://localhost:5000"
      eventbridge      = "http://localhost:5000"
      iam              = "http://localhost:5000"
      lambda           = "http://localhost:5000"
      logs             = "http://localhost:5000"
      route53          = "http://localhost:5000"
      s3               = "http://localhost:5000"
      ssm              = "http://localhost:5000"
      sts              = "http://localhost:5000"
  }
}

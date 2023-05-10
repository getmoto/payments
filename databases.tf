resource "aws_dynamodb_table" "user-tokens" {
  name           = "UserTokens"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "access_token"

  attribute {
    name = "access_token"
    type = "S"
  }

  attribute {
    name = "state"
    type = "S"
  }

  ttl {
    attribute_name = "expiration"
    enabled        = false
  }

  global_secondary_index {
    name               = "OAuthState"
    hash_key           = "state"
    projection_type    = "KEYS_ONLY"
  }

  tags = {
    Project        = "payments"
  }
}


resource "aws_dynamodb_table" "pull-requests" {
  name           = "PullRequests"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "username"
  range_key      = "pr_nr"

  attribute {
    name = "username"
    type = "S"
  }

  attribute {
    name = "pr_nr"
    type = "S"
  }

  tags = {
    Project        = "payments"
  }
}

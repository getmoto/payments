resource "aws_dynamodb_table" "user-tokens" {
  name           = "UserTokens"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "access_token"

  attribute {
    name = "access_token"
    type = "S"
  }

  attribute {
    name = "username"
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
    Project        = "moneys"
  }
}


resource pull_requests

username
title
number
approved
merged
money
expense_received
expense_accepted (NONE/TRUE/FALSE)

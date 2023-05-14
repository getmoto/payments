locals {
  current_time           = timestamp()
  half_year_ago         = formatdate("YYYY-MM-DD", timeadd(local.current_time, "-4320h")) # 6 months ago
}

resource "aws_dynamodb_table" "user-tokens" {
  name           = "UserTokens"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "access_token"

  attribute {
    name = "access_token"
    type = "S"
  }

  ttl {
    attribute_name = "expiration"
    enabled        = true
  }

  tags = {
    Project        = "payments"
  }
}

resource "aws_dynamodb_table" "oauth-state" {
  name           = "OAuthState"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "state"

  attribute {
    name = "state"
    type = "S"
  }

  ttl {
    attribute_name = "expiration"
    enabled        = true
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

  # Select specific PR (to update)
  attribute {
    name = "pr_nr"
    type = "N"
  }

  attribute {
    name = "last_updated"
    type = "S"
  }

  # Query all recent PR's
  local_secondary_index {
    name            = "query_on_date"
    projection_type = "ALL"
    range_key       = "last_updated"
  }

  tags = {
    Project        = "payments"
  }
}

resource "aws_dynamodb_table" "script-execution-info" {
  name         = "ScriptExecutionInfo"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "script_name"

  attribute {
    name = "script_name"
    type = "S"
  }
}

resource "aws_dynamodb_table_item" "example" {
  table_name = aws_dynamodb_table.script-execution-info.name
  hash_key   = aws_dynamodb_table.script-execution-info.hash_key

  item = <<ITEM
{
  "script_name": {"S": "LOAD_PR_INFO"},
  "earliest_modify_date": {"S": "${local.half_year_ago}"}
}
ITEM
}

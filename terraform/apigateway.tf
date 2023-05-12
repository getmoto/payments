resource "aws_apigatewayv2_api" "payments-api" {
  name          = "payments-api"
  protocol_type = "HTTP"

  tags = {
    Project        = "payments"
  }
}

resource "aws_apigatewayv2_integration" "get_pr_info_route" {
  api_id                 = aws_apigatewayv2_api.payments-api.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.lambda_function_user_area.arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "get_pr_info_route" {
  api_id    = aws_apigatewayv2_api.payments-api.id
  route_key = "GET /pr_info"
  target    = "integrations/${aws_apigatewayv2_integration.get_pr_info_route.id}"
}

resource "aws_apigatewayv2_integration" "post_settings_route" {
  api_id                 = aws_apigatewayv2_api.payments-api.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.lambda_function_user_area.arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "post_settings_route" {
  api_id    = aws_apigatewayv2_api.payments-api.id
  route_key = "POST /settings"
  target    = "integrations/${aws_apigatewayv2_integration.post_settings_route.id}"
}

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.payments-api.id
  name        = "$default"
  auto_deploy = true
  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.api_gateway_payments.arn
    format          = jsonencode({ "requestId" : "$context.requestId", "ip" : "$context.identity.sourceIp", "requestTime" : "$context.requestTime", "httpMethod" : "$context.httpMethod", "routeKey" : "$context.routeKey", "status" : "$context.status", "protocol" : "$context.protocol", "responseLength" : "$context.responseLength" })
  }
}

resource "aws_cloudwatch_log_group" "api_gateway_payments" {
  name              = "/aws/apigateway/PaymentsAPI"
  retention_in_days = 7
}

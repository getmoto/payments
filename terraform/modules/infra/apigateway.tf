locals {
  apigw_origin_id = "PaymentsAPIOrigin"
}

resource "aws_apigatewayv2_authorizer" "authorize_user_area" {
  api_id                            = aws_apigatewayv2_api.payments-api.id
  authorizer_type                   = "REQUEST"
  authorizer_uri                    = aws_lambda_function.lambda_function_auth.invoke_arn
  identity_sources                  = ["$request.header.Cookie"]
  name                              = "example-authorizer"
  authorizer_payload_format_version = "2.0"
  enable_simple_responses           = true
}

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
  authorization_type = "CUSTOM"
  authorizer_id = aws_apigatewayv2_authorizer.authorize_user_area.id
}

resource "aws_apigatewayv2_integration" "get_payment_info_route" {
  api_id                 = aws_apigatewayv2_api.payments-api.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.lambda_function_user_area.arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "get_payment_info_route" {
  api_id    = aws_apigatewayv2_api.payments-api.id
  route_key = "GET /payment_info"
  target    = "integrations/${aws_apigatewayv2_integration.get_payment_info_route.id}"
  authorization_type = "CUSTOM"
  authorizer_id = aws_apigatewayv2_authorizer.authorize_user_area.id
}

resource "aws_apigatewayv2_integration" "get_status_route" {
  api_id                 = aws_apigatewayv2_api.payments-api.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.lambda_function_auth.arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "get_status_route" {
  api_id    = aws_apigatewayv2_api.payments-api.id
  route_key = "GET /status"
  target    = "integrations/${aws_apigatewayv2_integration.get_status_route.id}"
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
  authorization_type = "CUSTOM"
  authorizer_id = aws_apigatewayv2_authorizer.authorize_user_area.id
}

resource "aws_apigatewayv2_integration" "login_route" {
  api_id                 = aws_apigatewayv2_api.payments-api.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.lambda_function_auth.arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "login_route" {
  api_id    = aws_apigatewayv2_api.payments-api.id
  route_key = "GET /login"
  target    = "integrations/${aws_apigatewayv2_integration.login_route.id}"
}

resource "aws_apigatewayv2_integration" "logged_in_route" {
  api_id                 = aws_apigatewayv2_api.payments-api.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.lambda_function_auth.arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "logged_in_route" {
  api_id    = aws_apigatewayv2_api.payments-api.id
  route_key = "GET /logged_in"
  target    = "integrations/${aws_apigatewayv2_integration.logged_in_route.id}"
}

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.payments-api.id
  name        = "api"
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

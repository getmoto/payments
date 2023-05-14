variable "lambda_root" {
  type        = string
  description = "The relative path to the source of the lambda"
  default     = "backend/"
}

data "aws_iam_policy_document" "lambda_assume_role_policy"{
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com", "edgelambda.amazonaws.com"]
    }
  }
}

data "aws_iam_policy_document" "lambda_logging" {
  statement {
    effect = "Allow"

    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
    ]

    resources = ["arn:aws:logs:*:*:*"]
  }
}

resource "aws_iam_policy" "lambda_logging" {
  name        = "lambda_logging"
  path        = "/"
  description = "IAM policy for logging from a lambda"
  policy      = data.aws_iam_policy_document.lambda_logging.json
}

resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_logging.arn
}

data "aws_iam_policy_document" "lambda_service_access" {
  statement {
    effect = "Allow"

    actions = [
      "dynamodb:Scan",
      "dynamodb:GetItem",
      "dynamodb:UpdateItem",
      "dynamodb:PutItem",
      "dynamodb:BatchWriteItem"
    ]

    resources = ["arn:aws:dynamodb:*:*:*"]
  }

  statement {
    effect = "Allow"

    actions = [
      "ssm:GetParameter"
    ]

    resources = ["*"]
  }
}

resource "aws_iam_policy" "lambda_service_access" {
  name        = "lambda_service_access"
  path        = "/"
  description = "IAM policy detailing which services Lambda functions can access"
  policy      = data.aws_iam_policy_document.lambda_service_access.json
}

resource "aws_iam_role_policy_attachment" "lambda_service_access" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_service_access.arn
}

resource "aws_iam_role" "lambda_role" {
  name = "lambda-lambdaRole"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role_policy.json
}

resource "null_resource" "install_dependencies" {
  provisioner "local-exec" {
    command = "pip install -r ${var.lambda_root}/requirements.txt -t ${var.lambda_root}/"
  }

  triggers = {
    dependencies_versions = filemd5("${var.lambda_root}/requirements.txt")
    source_versions = filemd5("${var.lambda_root}/load_pr_info.py")
  }
}

resource "random_uuid" "lambda_hash_load_pr_info" {
  keepers = {
  for filename in setunion(
  fileset(var.lambda_root, "load_pr_info.py"),
  fileset(var.lambda_root, "query_github.py"),
  fileset(var.lambda_root, "requirements.txt")
  ) :
  filename => filemd5("${var.lambda_root}/${filename}")
  }
}

data "archive_file" "lambda_load-pr_package" {
  depends_on = [null_resource.install_dependencies]
  excludes   = [
    "__pycache__",
    "venv",
    "authentication.py",
    "requirements.txt",
    "user_area.py"
  ]

  source_dir  = var.lambda_root
  output_path = "lambda_zips/${random_uuid.lambda_hash_load_pr_info.result}.zip"
  type        = "zip"
}

resource "aws_lambda_function" "lambda_function_load_pr_info" {
  function_name = "LoadPullRequestInfo"
  filename      = data.archive_file.lambda_load-pr_package.output_path
  source_code_hash = data.archive_file.lambda_load-pr_package.output_base64sha256
  role          = aws_iam_role.lambda_role.arn
  runtime       = "python3.10"
  handler       = "load_pr_info.lambda_handler"
  timeout       = 60
  environment {
    variables = {
      PR_TABLE_NAME = aws_dynamodb_table.pull-requests.name
      SCRIPT_INFO_TABLE_NAME = aws_dynamodb_table.script-execution-info.name
    }
  }
}

resource "aws_cloudwatch_log_group" "lambda_load_pr_info" {
  name              = "/aws/lambda/LoadPullRequestInfo"
  retention_in_days = 7
}

resource "random_uuid" "lambda_hash_auth" {
  keepers = {
  for filename in setunion(
  fileset(var.lambda_root, "authentication.py"),
  fileset(var.lambda_root, "requirements.txt")
  ) :
  filename => filemd5("${var.lambda_root}/${filename}")
  }
}

data "archive_file" "lambda_auth_package" {
  depends_on = [null_resource.install_dependencies]
  excludes   = [
    "__pycache__",
    "venv",
    "load_pr_info.py",
    "query_github.py",
    "cronjobs/export_tables",
    "requirements.txt"
  ]

  source_dir  = var.lambda_root
  output_path = "lambda_zips/${random_uuid.lambda_hash_auth.result}.zip"
  type        = "zip"
}

resource "aws_lambda_function" "lambda_function_auth" {
  function_name = "Auth"
  filename      = data.archive_file.lambda_auth_package.output_path
  source_code_hash = data.archive_file.lambda_auth_package.output_base64sha256
  role          = aws_iam_role.lambda_role.arn
  runtime       = "python3.9"
  handler       = "authentication.lambda_handler"
  timeout       = 5
  publish       = true
}

# Stored in SSM to avoid a cyclic dependency from CLoudFront and Lambda
# TODO: Remove once we switch to a full (non-CF) domain
resource "aws_ssm_parameter" "domain_name" {
  name  = "/moto/payments/domain_name"
  type  = "String"
  value = aws_cloudfront_distribution.website-cloudfront.domain_name
}

resource "aws_cloudwatch_log_group" "lambda_auth" {
  name              = "/aws/lambda/Auth"
  retention_in_days = 7
}

resource "aws_lambda_permission" "authentication" {
  statement_id  = "AllowAPIGatewayToAuthentication"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.lambda_function_auth.arn
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.payments-api.execution_arn}/*/*"
}

resource "random_uuid" "lambda_hash_user_area" {
  keepers = {
  for filename in setunion(
  fileset(var.lambda_root, "user_area.py"),
  ) :
  filename => filemd5("${var.lambda_root}/${filename}")
  }
}

data "archive_file" "lambda_user_area_package" {
  depends_on = [null_resource.install_dependencies]

  source_file  = "${var.lambda_root}/user_area.py"
  output_path = "lambda_zips/${random_uuid.lambda_hash_user_area.result}.zip"
  type        = "zip"
}

resource "aws_lambda_function" "lambda_function_user_area" {
  function_name = "UserArea"
  filename      = data.archive_file.lambda_user_area_package.output_path
  source_code_hash = data.archive_file.lambda_user_area_package.output_base64sha256
  role          = aws_iam_role.lambda_role.arn
  runtime       = "python3.10"
  handler       = "user_area.lambda_handler"
  timeout       = 5
}

resource "aws_cloudwatch_log_group" "lambda_user_area" {
  name              = "/aws/lambda/UserArea"
  retention_in_days = 7
}

resource "aws_lambda_permission" "user_area" {
  statement_id  = "AllowAPIGatewayToUserArea"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.lambda_function_user_area.arn
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.payments-api.execution_arn}/*/*"
}

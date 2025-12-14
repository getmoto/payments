variable "lambda_root" {
  type        = string
  description = "The relative path to the source of the lambda"
  default     = "../../../backend/"
}

variable "repo_owner_name" {
  type        = string
}

resource "null_resource" "install_jwt_dependencies" {
  provisioner "local-exec" {
    command = "pip install --platform manylinux2014_x86_64 --implementation cp --only-binary=:all: --upgrade --target ${var.lambda_root}/jwt_dependencies/python jwt"
  }

  triggers = {
    always_run = "20251214"
  }
}

data "archive_file" "lambda_jwt_layer" {
  depends_on = [null_resource.install_jwt_dependencies]

  source_dir  = "${var.lambda_root}/jwt_dependencies"
  output_path = "lambda_zips/jwt_layer.zip"
  type        = "zip"
}

resource "aws_lambda_layer_version" "jwt_layer" {
  depends_on = [data.archive_file.lambda_jwt_layer]
  filename   = data.archive_file.lambda_jwt_layer.output_path
  layer_name = "jwt_dependencies_2"

  compatible_runtimes = ["python3.13"]
}

data "aws_iam_policy_document" "lambda_assume_role_policy"{
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
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
  name        = "${var.resource_prefix}lambda_logging"
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
      "dynamodb:BatchWriteItem",
      "dynamodb:Query",
      "dynamodb:DeleteItem"
    ]

    resources = ["arn:aws:dynamodb:*:*:*"]
  }

  statement {
    effect = "Allow"

    actions = [
      "ssm:GetParameter",
      "ssm:GetParametersByPath"
    ]

    resources = ["*"]
  }
}

resource "aws_iam_policy" "lambda_service_access" {
  name        = "${var.resource_prefix}lambda_service_access"
  path        = "/"
  description = "IAM policy detailing which services Lambda functions can access"
  policy      = data.aws_iam_policy_document.lambda_service_access.json
}

resource "aws_iam_role_policy_attachment" "lambda_service_access" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_service_access.arn
}

resource "aws_iam_role" "lambda_role" {
  name = "${var.resource_prefix}lambda-lambdaRole"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role_policy.json
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
  excludes   = [
    "authentication.py",
    "backup_payment_data.py",
    "expiring_dict.py",
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
  runtime       = "python3.13"
  handler       = "load_pr_info.lambda_handler"
  timeout       = 60
  environment {
    variables = {
      REGION = data.aws_region.current.region
      PR_TABLE_NAME = aws_dynamodb_table.pull-requests.name
      SCRIPT_INFO_TABLE_NAME = aws_dynamodb_table.script-execution-info.name
      REPO_OWNER_NAME = var.repo_owner_name
    }
  }
  depends_on = [aws_cloudwatch_log_group.lambda_load_pr_info]
}

resource "aws_cloudwatch_log_group" "lambda_load_pr_info" {
  name              = "/aws/lambda/LoadPullRequestInfo"
  retention_in_days = 7
}

resource "aws_cloudwatch_event_rule" "load_pr_lambda_event_rule" {
  name = "load-pr-lambda-event-rule"
  description = "Load PR's from GitHub"
  schedule_expression = "rate(12 hours)"
}

resource "aws_cloudwatch_event_target" "load_pr_lambda_target" {
  arn = aws_lambda_function.lambda_function_load_pr_info.arn
  rule = aws_cloudwatch_event_rule.load_pr_lambda_event_rule.name
}

resource "aws_lambda_permission" "load_pr_event_permission" {
  statement_id = "AllowExecutionFromCloudWatch"
  action = "lambda:InvokeFunction"
  function_name = aws_lambda_function.lambda_function_load_pr_info.function_name
  principal = "events.amazonaws.com"
  source_arn = aws_cloudwatch_event_rule.load_pr_lambda_event_rule.arn
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
  excludes   = [
    "__init__.py",
    "admin_area.py",
    "backup_payment_data.py",
    "load_pr_info.py",
    "query_github.py",
    "requirements.txt",
    "user_area.py"
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
  runtime       = "python3.13"
  handler       = "authentication.lambda_handler"
  timeout       = 5
  depends_on    = [aws_cloudwatch_log_group.lambda_auth]
  environment {
    variables = {
      REGION = data.aws_region.current.region
      DOMAIN_NAME = var.domain
      REPO_OWNER_NAME = var.repo_owner_name
    }
  }
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
  source_file  = "${var.lambda_root}/user_area.py"
  output_path = "lambda_zips/${random_uuid.lambda_hash_user_area.result}.zip"
  type        = "zip"
}

resource "aws_lambda_function" "lambda_function_user_area" {
  function_name = "UserArea"
  filename      = data.archive_file.lambda_user_area_package.output_path
  source_code_hash = data.archive_file.lambda_user_area_package.output_base64sha256
  role          = aws_iam_role.lambda_role.arn
  runtime       = "python3.13"
  handler       = "user_area.lambda_handler"
  timeout       = 5
  depends_on    = [aws_cloudwatch_log_group.lambda_user_area]
  environment {
    variables = {
      REGION = data.aws_region.current.region
      REPO_OWNER_NAME = var.repo_owner_name
    }
  }
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

resource "aws_lambda_function" "payments_info_backup" {
  function_name    = "PaymentsTableBackup"
  filename         = data.archive_file.payment_info_backup_files.output_path
  source_code_hash = data.archive_file.payment_info_backup_files.output_base64sha256
  handler          = "backup_payment_data.handler"
  role             = aws_iam_role.lambda_assume_role.arn
  runtime          = "python3.13"
  depends_on       = [aws_cloudwatch_log_group.payments_backup]
  environment {
    variables = {
      BACKUP_BUCKET_NAME = aws_s3_bucket.website-backup.bucket
    }
  }
}

resource "aws_cloudwatch_log_group" "payments_backup" {
  name              = "/aws/lambda/PaymentsTableBackup"
  retention_in_days = 7
}

data "archive_file" "payment_info_backup_files" {
  output_path = "lambda_zips/payment_info_backup_files.zip"
  source_file = "${var.lambda_root}/backup_payment_data.py"
  type        = "zip"
}

resource "random_uuid" "lambda_hash_admin_area" {
  keepers = {
  for filename in setunion(
  fileset(var.lambda_root, "admin_area.py"),
  ) :
  filename => filemd5("${var.lambda_root}/${filename}")
  }
}

data "archive_file" "lambda_admin_area_package" {
  excludes   = [
    "__init__.py",
    "authentication.py",
    "backup_payment_data.py",
    "load_pr_info.py",
    "requirements.txt",
    "user_area.py"
  ]

  source_dir  = var.lambda_root
  output_path = "lambda_zips/${random_uuid.lambda_hash_admin_area.result}.zip"
  type        = "zip"
}

resource "aws_lambda_function" "lambda_function_admin_area" {
  function_name = "AdminArea"
  filename      = data.archive_file.lambda_admin_area_package.output_path
  source_code_hash = data.archive_file.lambda_admin_area_package.output_base64sha256
  role          = aws_iam_role.lambda_role.arn
  runtime       = "python3.13"
  handler       = "admin_area.lambda_handler"
  timeout       = 10
  depends_on    = [aws_cloudwatch_log_group.lambda_admin_area]
  layers        = [aws_lambda_layer_version.jwt_layer.arn]
  environment {
    variables = {
      REGION = data.aws_region.current.region
      REPO_OWNER_NAME = var.repo_owner_name
    }
  }
}

resource "aws_cloudwatch_log_group" "lambda_admin_area" {
  name              = "/aws/lambda/AdminArea"
  retention_in_days = 7
}

resource "aws_lambda_permission" "admin_area" {
  statement_id  = "AllowAPIGatewayToAdminArea"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.lambda_function_admin_area.arn
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.payments-api.execution_arn}/*/*"
}

resource "aws_iam_role" "lambda_assume_role" {
  name               = "${var.resource_prefix}lambda-dynamodb-role"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": "LambdaAssumeRole"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy" "dynamodb_read_log_policy" {
  name   = "lambda-dynamodb-log-policy"
  role   = aws_iam_role.lambda_assume_role.id
  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
        "Action": [ "logs:*" ],
        "Effect": "Allow",
        "Resource": [ "arn:aws:logs:*:*:*" ]
    },
    {
        "Action": [ "dynamodb:BatchGetItem",
                    "dynamodb:GetItem",
                    "dynamodb:GetRecords",
                    "dynamodb:Scan",
                    "dynamodb:Query",
                    "dynamodb:GetShardIterator",
                    "dynamodb:DescribeStream",
                    "dynamodb:ListStreams" ],
        "Effect": "Allow",
        "Resource": [
          "${aws_dynamodb_table.payment-info.arn}",
          "${aws_dynamodb_table.payment-info.arn}/*"
        ]
    },
    {
        "Action": [ "s3:PutObject"],
        "Effect": "Allow",
        "Resource": ["*"]
    }
  ]
}
EOF
}

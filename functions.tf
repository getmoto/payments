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
      identifiers = ["lambda.amazonaws.com"]
    }
  }
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
    "authenticate.py",
    "login.py",
    "requirements.txt",
    "get_pr_info.py"
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
  timeout       = 600
}

resource "random_uuid" "lambda_hash_auth" {
  keepers = {
  for filename in setunion(
  fileset(var.lambda_root, "load_pr_info.py"),
  fileset(var.lambda_root, "query_github.py"),
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
  runtime       = "python3.10"
  handler       = "authenticate.lambda_handler"
  timeout       = 5
}

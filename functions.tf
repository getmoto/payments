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

data "archive_file" "lambda_load-pr_package" {
  type = "zip"
  # TODO: add query_github.py and dependencies from requirements.txt
  source_file = "${path.module}/backend/load_pr_info.py"
  output_path = "load_pr_info.zip"
}

resource "aws_lambda_function" "test_lambda_function" {
  function_name = "LoadPullRequestInfo"
  filename      = "load_pr_info.zip"
  source_code_hash = data.archive_file.lambda_load-pr_package.output_base64sha256
  role          = aws_iam_role.lambda_role.arn
  runtime       = "python3.10"
  handler       = "load_pr_info.lambda_handler"
  timeout       = 10
}

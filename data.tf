data "aws_caller_identity" "current" {}

locals {
    account_id = data.aws_caller_identity.current.account_id
}

data "aws_iam_policy_document" "allow_cloudfront_access_to_fe" {
  statement {
    sid = "AllowCloudFrontAccessToFE"
    principals {
      type          = "Service"
      identifiers   = ["cloudfront.amazonaws.com"]
    }

    actions = [
      "s3:GetObject"
    ]

    resources = [
      aws_s3_bucket.website-fe.arn,
      "${aws_s3_bucket.website-fe.arn}/*",
    ]

    condition {
      test     = "StringEquals"
      variable = "AWS:SourceArn"

      values = [
        "arn:aws:cloudfront::${local.account_id}:distribution/aws_cloudfront_distribution.website-cloudfront.id"
      ]
    }
  }
}

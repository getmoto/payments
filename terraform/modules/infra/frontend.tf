resource "aws_s3_bucket" "website-fe" {
  bucket = "moto-payments-website-fe"

  tags = {
    Project     = "payments"
  }
}

module "template_files" {
  source = "hashicorp/dir/template"

  base_dir = "${path.module}/../../../website"
}

resource "aws_s3_object" "website-fe-files" {
  for_each = module.template_files.files

    bucket = aws_s3_bucket.website-fe.id
    key = each.key
    content_type = each.value.content_type

    source = each.value.source_path
    etag = each.value.digests.md5
    tags = {
      Project  =  "payments"
    }
}

locals {
  s3_origin_id = "PaymentsWebsiteOrigin"
}

resource "aws_s3_bucket_policy" "website-fe-policy" {
  bucket = aws_s3_bucket.website-fe.id
  policy = data.aws_iam_policy_document.allow_cloudfront_access_to_fe.json
}

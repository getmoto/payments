resource "aws_cloudfront_origin_access_control" "website" {
  name                              = "CF Origin Access Control"
  description                       = "Example Policy"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

resource "aws_cloudfront_distribution" "website-cloudfront" {
  # Disable for now, as creation takes a long time during testing
  # Also re-enable the IAM policy document in data.tf
  count             = 0

  origin {
    domain_name              = aws_s3_bucket.website-fe.bucket_regional_domain_name
    origin_access_control_id = aws_cloudfront_origin_access_control.website.id
    origin_id                = local.s3_origin_id
  }

  enabled             = true
  is_ipv6_enabled     = true
  comment             = "Cloudfront Distribution for S3"
  default_root_object = "index.html"

  logging_config {
    include_cookies = false
    bucket          = "${aws_s3_bucket.website-logging.bucket_domain_name}"
    prefix          = "cloudfront"
  }

  # aliases = ["mysite.example.com", "yoursite.example.com"]

  default_cache_behavior {
    allowed_methods  = ["HEAD", "GET", "OPTIONS"]
    cached_methods   = ["HEAD", "GET"]
    target_origin_id = local.s3_origin_id

    forwarded_values {
      query_string = false

      cookies {
        forward = "none"
      }
    }

    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 3600
    max_ttl                = 86400
  }

  price_class = "PriceClass_100"

  tags = {
    Project  =   "payments"
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }
}

resource "aws_s3_bucket" "website-logging" {
  bucket = "moto-payments-website-logging"

  tags = {
    Project     = "payments"
  }
}

resource "aws_s3_bucket_ownership_controls" "website-logging" {
  bucket = aws_s3_bucket.website-logging.id
  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_acl" "website-logging" {
  bucket = aws_s3_bucket.website-logging.id
  acl    = "private"
  depends_on = [aws_s3_bucket_ownership_controls.website-logging]
}

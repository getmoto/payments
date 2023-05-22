resource "aws_cloudfront_origin_access_control" "website" {
  name                              = "CF Origin Access Control"
  description                       = "Example Policy"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

resource "aws_cloudfront_distribution" "website-cloudfront" {

  origin {
    domain_name              = aws_s3_bucket.website-fe.bucket_regional_domain_name
    origin_access_control_id = aws_cloudfront_origin_access_control.website.id
    origin_id                = local.s3_origin_id
  }

  origin {
    domain_name = "${aws_apigatewayv2_api.payments-api.id}.execute-api.${data.aws_region.current.name}.amazonaws.com"
    origin_id   = local.apigw_origin_id
    custom_origin_config {
      http_port              = "80"
      https_port             = "443"
      origin_protocol_policy = "https-only"
      origin_ssl_protocols   = ["TLSv1.2"]
    }
  }

  enabled             = true
  is_ipv6_enabled     = true
  comment             = "Cloudfront Distribution for S3"
  default_root_object = "index.html"

  logging_config {
    include_cookies = false
    bucket          = aws_s3_bucket.website-logging.bucket_domain_name
    prefix          = "cloudfront"
  }

  aliases = [var.domain]

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
    # Testing
    min_ttl                = 0
    default_ttl            = 10
    max_ttl                = 10
  }

  # Redirect to API Gateway
  ordered_cache_behavior {
    path_pattern     = "/api/*"
    allowed_methods  = ["GET", "HEAD", "OPTIONS", "PUT", "POST", "PATCH", "DELETE"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = local.apigw_origin_id

    forwarded_values {
      query_string = true

      cookies {
        forward = "all"
      }
    }

    min_ttl                = 0
    default_ttl            = 0
    max_ttl                = 0
    viewer_protocol_policy = "https-only"
  }

  price_class = "PriceClass_100"

  tags = {
    Project  =   "payments"
  }

  viewer_certificate {
    acm_certificate_arn = aws_acm_certificate.payments_getmoto_org.arn
    ssl_support_method = "sni-only"
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

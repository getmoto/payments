variable "domain" {
  default = "payments.getmoto.org"
}

resource "aws_acm_certificate" "payments_getmoto_org" {
  domain_name       = var.domain
  validation_method = "DNS"

  tags = {
    Project  =   "payments"
  }

  lifecycle {
    create_before_destroy = true
  }
}

data "aws_route53_zone" "getmoto_org" {
  name         = "getmoto.org"
  private_zone = false
}

resource "aws_route53_record" "root_domain" {
  zone_id = data.aws_route53_zone.getmoto_org.zone_id
  name = var.domain
  type = "A"

  alias {
    name = aws_cloudfront_distribution.website-cloudfront.domain_name
    zone_id = aws_cloudfront_distribution.website-cloudfront.hosted_zone_id
    evaluate_target_health = false
  }
}

resource "aws_route53_record" "example" {
  for_each = {
    for dvo in aws_acm_certificate.payments_getmoto_org.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  }

  allow_overwrite = true
  name            = each.value.name
  records         = [each.value.record]
  ttl             = 60
  type            = each.value.type
  zone_id         = data.aws_route53_zone.getmoto_org.zone_id
}

resource "aws_acm_certificate_validation" "example" {
  certificate_arn         = aws_acm_certificate.payments_getmoto_org.arn
  validation_record_fqdns = [for record in aws_route53_record.example : record.fqdn]
}

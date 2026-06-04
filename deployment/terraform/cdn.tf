locals {
  frontend_bucket_name = "${lower(replace(var.project, " ", ""))}-${lower(var.environment)}-frontend-${var.aws_region}"
  api_cache_behaviors = [
    {
      path_pattern = "api/facilities/*"
      default_ttl  = var.api_facilities_cache_default_ttl
      max_ttl      = var.api_facilities_cache_max_ttl
    },
    {
      path_pattern = "api/v1/production-locations*"
      default_ttl  = var.api_production_locations_cache_default_ttl
      max_ttl      = var.api_production_locations_cache_max_ttl
    },
    {
      path_pattern = "api/partner-field-groups/*"
      default_ttl  = var.api_partner_field_groups_cache_default_ttl
      max_ttl      = var.api_partner_field_groups_cache_max_ttl
    },
    {
      path_pattern = "api/partner-fields/*"
      default_ttl  = var.api_partner_fields_cache_default_ttl
      max_ttl      = var.api_partner_fields_cache_max_ttl
    },
    {
      path_pattern = "api/partner-group-contributors*"
      default_ttl  = var.api_partner_group_contributors_cache_default_ttl
      max_ttl      = var.api_partner_group_contributors_cache_max_ttl
    },
    {
      path_pattern = "api/contributors/"
      default_ttl  = var.api_contributors_cache_default_ttl
      max_ttl      = var.api_contributors_cache_max_ttl
    },
    {
      path_pattern = "api/contributor-lists-sorted/*"
      default_ttl  = var.api_contributor_lists_sorted_cache_default_ttl
      max_ttl      = var.api_contributor_lists_sorted_cache_max_ttl
    },
    {
      path_pattern = "api/parent-companies/*"
      default_ttl  = var.api_parent_companies_cache_default_ttl
      max_ttl      = var.api_parent_companies_cache_max_ttl
    }
  ]
}

resource "aws_s3_bucket" "react" {
  bucket        = local.frontend_bucket_name
  force_destroy = true

  tags = {
    Name = local.frontend_bucket_name
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "react" {
  bucket = aws_s3_bucket.react.id

  rule {
    bucket_key_enabled = false

    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_versioning" "react" {
  bucket = aws_s3_bucket.react.id

  versioning_configuration {
    status = "Disabled"
  }
}

resource "aws_s3_bucket_ownership_controls" "react" {
  bucket = aws_s3_bucket.react.id

  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

resource "aws_s3_bucket_public_access_block" "react" {
  bucket = aws_s3_bucket.react.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

data "aws_iam_policy_document" "react" {
  statement {
    sid    = "denyInsecureTransport"
    effect = "Deny"

    actions = [
      "s3:*",
    ]

    resources = [
      aws_s3_bucket.react.arn,
      "${aws_s3_bucket.react.arn}/*",
    ]

    principals {
      type        = "*"
      identifiers = ["*"]
    }

    condition {
      test     = "Bool"
      variable = "aws:SecureTransport"
      values = [
        "false"
      ]
    }
  }

  statement {
    sid = "CloudFront"
    principals {
      identifiers = [
        aws_cloudfront_origin_access_identity.react.iam_arn
      ]
      type = "AWS"
    }
    actions   = ["s3:GetObject"]
    resources = ["${aws_s3_bucket.react.arn}/*"]
  }
}

resource "aws_s3_bucket_policy" "react" {
  bucket = aws_s3_bucket.react.id
  policy = data.aws_iam_policy_document.react.json
}

resource "aws_cloudfront_origin_access_identity" "react" {
  comment = local.frontend_bucket_name
}

resource "aws_cloudfront_distribution" "cdn" {
  depends_on = [
    aws_s3_bucket.logs,
    aws_s3_bucket.react
  ]

  default_root_object = "index.html"

  origin {
    domain_name = "origin.${local.domain_name}"
    origin_id   = "originAlb"

    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "https-only"
      origin_ssl_protocols   = ["TLSv1", "TLSv1.1", "TLSv1.2"]
    }

    custom_header {
      name  = "X-CloudFront-Auth"
      value = var.cloudfront_auth_token
    }
  }

  origin {
    domain_name = aws_s3_bucket.react.bucket_regional_domain_name
    origin_id   = "originS3"

    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.react.cloudfront_access_identity_path
    }

    custom_header {
      name  = "X-CloudFront-Auth"
      value = var.cloudfront_auth_token
    }
  }

  enabled         = true
  is_ipv6_enabled = true
  http_version    = "http2"
  comment         = "${var.project} (${var.environment})"

  price_class = var.cloudfront_price_class
  aliases     = [local.domain_name]

  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "originS3"

    forwarded_values {
      query_string = true
      headers      = []

      cookies {
        forward = "all"
      }
    }

    lambda_function_association {
      event_type = "viewer-request"
      lambda_arn = aws_lambda_function.redirect_to_s3_origin.qualified_arn
    }

    lambda_function_association {
      event_type   = "viewer-response"
      lambda_arn   = aws_lambda_function.add_security_headers.qualified_arn
      include_body = false
    }

    compress               = false
    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 0
    max_ttl                = 300
  }

  ordered_cache_behavior {
    path_pattern     = "tile/*"
    allowed_methods  = ["GET", "HEAD", "OPTIONS"]
    cached_methods   = ["GET", "HEAD", "OPTIONS"]
    target_origin_id = "originAlb"

    forwarded_values {
      query_string = true
      headers      = ["Referer"]

      cookies {
        forward = "none"
      }
    }

    compress               = true
    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 3600
    max_ttl                = 31536000 # 1 year. Same as TILE_CACHE_MAX_AGE_IN_SECONDS in src/django/oar/settings.py
  }

  dynamic "ordered_cache_behavior" {
    for_each = local.api_cache_behaviors

    content {
      path_pattern     = ordered_cache_behavior.value.path_pattern
      allowed_methods  = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
      cached_methods   = ["GET", "HEAD", "OPTIONS"]
      target_origin_id = "originAlb"

      forwarded_values {
        query_string = true
        headers = [
          "Host",
          "Authorization",
          "X-OAR-CLIENT-KEY",
          "Referer",
        ]

        cookies {
          forward           = "whitelist"
          whitelisted_names = ["sessionid", "csrftoken"]
        }
      }

      compress               = true
      viewer_protocol_policy = "redirect-to-https"
      min_ttl                = 0
      default_ttl            = ordered_cache_behavior.value.default_ttl
      max_ttl                = ordered_cache_behavior.value.max_ttl
    }
  }

  ordered_cache_behavior {
    path_pattern     = "api/*"
    allowed_methods  = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods   = ["GET", "HEAD", "OPTIONS"]
    target_origin_id = "originAlb"

    forwarded_values {
      query_string = true
      headers      = ["*"]

      cookies {
        forward = "all"
      }
    }

    compress               = true
    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 0
    max_ttl                = 300
  }

  ordered_cache_behavior {
    path_pattern     = "/api-auth/*"
    allowed_methods  = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods   = ["GET", "HEAD", "OPTIONS"]
    target_origin_id = "originAlb"

    forwarded_values {
      query_string = true
      headers      = ["*"]

      cookies {
        forward = "all"
      }
    }

    compress               = true
    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 0
    max_ttl                = 300
  }

  ordered_cache_behavior {
    path_pattern     = "/api-token-auth/*"
    allowed_methods  = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods   = ["GET", "HEAD", "OPTIONS"]
    target_origin_id = "originAlb"

    forwarded_values {
      query_string = true
      headers      = ["*"]

      cookies {
        forward = "all"
      }
    }

    compress               = true
    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 0
    max_ttl                = 300
  }

  ordered_cache_behavior {
    path_pattern     = "/api-feature-flags/*"
    allowed_methods  = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods   = ["GET", "HEAD", "OPTIONS"]
    target_origin_id = "originAlb"

    forwarded_values {
      query_string = true
      headers      = ["*"]

      cookies {
        forward = "all"
      }
    }

    compress               = true
    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 0
    max_ttl                = 300
  }

  ordered_cache_behavior {
    path_pattern     = "/web/environment.js"
    allowed_methods  = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods   = ["GET", "HEAD", "OPTIONS"]
    target_origin_id = "originAlb"

    forwarded_values {
      query_string = true
      headers      = ["*"]

      cookies {
        forward = "all"
      }
    }

    compress               = true
    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 0
    max_ttl                = 300
  }

  ordered_cache_behavior {
    path_pattern     = "/admin/*"
    allowed_methods  = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods   = ["GET", "HEAD", "OPTIONS"]
    target_origin_id = "originAlb"

    forwarded_values {
      query_string = true
      headers      = ["*"]

      cookies {
        forward = "all"
      }
    }

    compress               = true
    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 0
    max_ttl                = 300
  }

  ordered_cache_behavior {
    path_pattern     = "/health-check/*"
    allowed_methods  = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods   = ["GET", "HEAD", "OPTIONS"]
    target_origin_id = "originAlb"

    forwarded_values {
      query_string = true
      headers      = ["*"]

      cookies {
        forward = "all"
      }
    }

    compress               = true
    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 0
    max_ttl                = 300
  }

  ordered_cache_behavior {
    path_pattern     = "/rest-auth/*"
    allowed_methods  = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods   = ["GET", "HEAD", "OPTIONS"]
    target_origin_id = "originAlb"

    forwarded_values {
      query_string = true
      headers      = ["*"]

      cookies {
        forward = "all"
      }
    }

    compress               = true
    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 0
    max_ttl                = 300
  }

  ordered_cache_behavior {
    path_pattern     = "/user-login/*"
    allowed_methods  = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods   = ["GET", "HEAD", "OPTIONS"]
    target_origin_id = "originAlb"

    forwarded_values {
      query_string = true
      headers      = ["*"]

      cookies {
        forward = "all"
      }
    }

    compress               = true
    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 0
    max_ttl                = 300
  }

  ordered_cache_behavior {
    path_pattern     = "/user-logout/*"
    allowed_methods  = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods   = ["GET", "HEAD", "OPTIONS"]
    target_origin_id = "originAlb"

    forwarded_values {
      query_string = true
      headers      = ["*"]

      cookies {
        forward = "all"
      }
    }

    compress               = true
    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 0
    max_ttl                = 300
  }

  ordered_cache_behavior {
    path_pattern     = "/user-signup/*"
    allowed_methods  = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods   = ["GET", "HEAD", "OPTIONS"]
    target_origin_id = "originAlb"

    forwarded_values {
      query_string = true
      headers      = ["*"]

      cookies {
        forward = "all"
      }
    }

    compress               = true
    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 0
    max_ttl                = 300
  }

  ordered_cache_behavior {
    path_pattern     = "/user-profile/*"
    allowed_methods  = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods   = ["GET", "HEAD", "OPTIONS"]
    target_origin_id = "originAlb"

    forwarded_values {
      query_string = true
      headers      = ["*"]

      cookies {
        forward = "all"
      }
    }

    compress               = true
    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 0
    max_ttl                = 300
  }

  ordered_cache_behavior {
    path_pattern     = "/user-api-info/*"
    allowed_methods  = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods   = ["GET", "HEAD", "OPTIONS"]
    target_origin_id = "originAlb"

    forwarded_values {
      query_string = true
      headers      = ["*"]

      cookies {
        forward = "all"
      }
    }

    compress               = true
    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 0
    max_ttl                = 300
  }

  ordered_cache_behavior {
    path_pattern     = "/admin"
    allowed_methods  = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods   = ["GET", "HEAD", "OPTIONS"]
    target_origin_id = "originAlb"

    forwarded_values {
      query_string = true
      headers      = ["*"]

      cookies {
        forward = "all"
      }
    }

    compress               = true
    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 0
    max_ttl                = 300
  }

  ordered_cache_behavior {
    path_pattern     = "/static/admin/*"
    allowed_methods  = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods   = ["GET", "HEAD", "OPTIONS"]
    target_origin_id = "originAlb"

    forwarded_values {
      query_string = true
      headers      = ["*"]

      cookies {
        forward = "all"
      }
    }

    compress               = true
    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 0
    max_ttl                = 300
  }

  ordered_cache_behavior {
    path_pattern     = "/static/django_extensions/*"
    allowed_methods  = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods   = ["GET", "HEAD", "OPTIONS"]
    target_origin_id = "originAlb"

    forwarded_values {
      query_string = true
      headers      = ["*"]

      cookies {
        forward = "all"
      }
    }

    compress               = true
    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 0
    max_ttl                = 300
  }

  ordered_cache_behavior {
    path_pattern     = "/static/drf-yasg/*"
    allowed_methods  = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods   = ["GET", "HEAD", "OPTIONS"]
    target_origin_id = "originAlb"

    forwarded_values {
      query_string = true
      headers      = ["*"]

      cookies {
        forward = "all"
      }
    }

    compress               = true
    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 0
    max_ttl                = 300
  }

  ordered_cache_behavior {
    path_pattern     = "/static/gis/*"
    allowed_methods  = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods   = ["GET", "HEAD", "OPTIONS"]
    target_origin_id = "originAlb"

    forwarded_values {
      query_string = true
      headers      = ["*"]

      cookies {
        forward = "all"
      }
    }

    compress               = true
    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 0
    max_ttl                = 300
  }

  ordered_cache_behavior {
    path_pattern     = "/static/rest_framework/*"
    allowed_methods  = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods   = ["GET", "HEAD", "OPTIONS"]
    target_origin_id = "originAlb"

    forwarded_values {
      query_string = true
      headers      = ["*"]

      cookies {
        forward = "all"
      }
    }

    compress               = true
    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 0
    max_ttl                = 300
  }

  ordered_cache_behavior {
    path_pattern     = "/static/static/*"
    allowed_methods  = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods   = ["GET", "HEAD", "OPTIONS"]
    target_origin_id = "originAlb"

    forwarded_values {
      query_string = true
      headers      = ["*"]

      cookies {
        forward = "all"
      }
    }

    compress               = true
    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 0
    max_ttl                = 300
  }

  ordered_cache_behavior {
    path_pattern     = "/static/staticfiles.json"
    allowed_methods  = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods   = ["GET", "HEAD", "OPTIONS"]
    target_origin_id = "originAlb"

    forwarded_values {
      query_string = true
      headers      = ["*"]

      cookies {
        forward = "all"
      }
    }

    compress               = true
    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 0
    max_ttl                = 300
  }

  ordered_cache_behavior {
    path_pattern     = "/static/django_ckeditor_5/*"
    allowed_methods  = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods   = ["GET", "HEAD", "OPTIONS"]
    target_origin_id = "originAlb"

    forwarded_values {
      query_string = true
      headers      = ["*"]

      cookies {
        forward = "all"
      }
    }

    compress               = true
    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 0
    max_ttl                = 300
  }

  ordered_cache_behavior {
    path_pattern     = "/static/*jsoneditor/*"
    allowed_methods  = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods   = ["GET", "HEAD", "OPTIONS"]
    target_origin_id = "originAlb"

    forwarded_values {
      query_string = true
      headers      = ["*"]

      cookies {
        forward = "all"
      }
    }

    compress               = true
    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 0
    max_ttl                = 300
  }

  logging_config {
    include_cookies = false
    bucket          = aws_s3_bucket.logs.bucket_domain_name
    prefix          = "CDN"
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    acm_certificate_arn      = module.cert_cdn.arn
    minimum_protocol_version = "TLSv1.2_2018"
    ssl_support_method       = "sni-only"
  }

  tags = {
    Project     = var.project
    Environment = var.environment
  }

  web_acl_id = var.waf_enabled ? aws_wafv2_web_acl.web_acl[var.environment].arn : null
}

#
# info.openapparel.org → https://info.opensupplyhub.org redirect (Production only)
#
data "aws_route53_zone" "openapparel" {
  count = var.environment == "Production" ? 1 : 0
  name  = "openapparel.org"
}

resource "aws_acm_certificate" "info_openapparel_redirect" {
  count             = var.environment == "Production" ? 1 : 0
  provider          = aws.certificates
  domain_name       = "info.openapparel.org"
  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_route53_record" "info_openapparel_cert_validation" {
  for_each = var.environment == "Production" ? {
    for dvo in aws_acm_certificate.info_openapparel_redirect[0].domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  } : {}

  zone_id = data.aws_route53_zone.openapparel[0].zone_id
  name    = each.value.name
  type    = each.value.type
  ttl     = 60
  records = [each.value.record]
}

resource "aws_acm_certificate_validation" "info_openapparel_redirect" {
  count                   = var.environment == "Production" ? 1 : 0
  provider                = aws.certificates
  certificate_arn         = aws_acm_certificate.info_openapparel_redirect[0].arn
  validation_record_fqdns = [for r in aws_route53_record.info_openapparel_cert_validation : r.fqdn]
}

resource "aws_cloudfront_function" "info_openapparel_redirect" {
  count   = var.environment == "Production" ? 1 : 0
  name    = "info-openapparel-org-redirect"
  runtime = "cloudfront-js-2.0"
  publish = true
  code    = <<-EOT
    function handler(event) {
      var qs = event.request.querystring;
      var location = "https://info.opensupplyhub.org" + event.request.uri + (qs ? "?" + qs : "");
      return {
        statusCode: 301,
        statusDescription: "Moved Permanently",
        headers: {
          location: { value: location }
        }
      };
    }
  EOT
}

resource "aws_cloudfront_distribution" "info_openapparel_redirect" {
  count           = var.environment == "Production" ? 1 : 0
  enabled         = true
  is_ipv6_enabled = true
  comment         = "Redirect info.openapparel.org to info.opensupplyhub.org"
  aliases         = ["info.openapparel.org"]

  origin {
    domain_name = "info.opensupplyhub.org"
    origin_id   = "info-opensupplyhub-origin"
    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "https-only"
      origin_ssl_protocols   = ["TLSv1.2"]
    }
  }

  default_cache_behavior {
    allowed_methods        = ["GET", "HEAD"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = "info-opensupplyhub-origin"
    viewer_protocol_policy = "redirect-to-https"
    compress               = false
    min_ttl                = 0
    default_ttl            = 0
    max_ttl                = 0

    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }

    function_association {
      event_type   = "viewer-request"
      function_arn = aws_cloudfront_function.info_openapparel_redirect[0].arn
    }
  }

  logging_config {
    include_cookies = false
    bucket          = aws_s3_bucket.logs.bucket_domain_name
    prefix          = "CDN-info-openapparel-redirect"
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    acm_certificate_arn      = aws_acm_certificate_validation.info_openapparel_redirect[0].certificate_arn
    minimum_protocol_version = "TLSv1.2_2021"
    ssl_support_method       = "sni-only"
  }

  tags = {
    Project     = var.project
    Environment = var.environment
  }

  web_acl_id = var.waf_enabled ? aws_wafv2_web_acl.web_acl[var.environment].arn : null
}

resource "aws_route53_record" "info_openapparel_redirect" {
  count   = var.environment == "Production" ? 1 : 0
  zone_id = data.aws_route53_zone.openapparel[0].zone_id
  name    = "info.openapparel.org"
  type    = "A"

  alias {
    name                   = aws_cloudfront_distribution.info_openapparel_redirect[0].domain_name
    zone_id                = aws_cloudfront_distribution.info_openapparel_redirect[0].hosted_zone_id
    evaluate_target_health = false
  }
}

resource "aws_route53_record" "info_openapparel_redirect_ipv6" {
  count   = var.environment == "Production" ? 1 : 0
  zone_id = data.aws_route53_zone.openapparel[0].zone_id
  name    = "info.openapparel.org"
  type    = "AAAA"

  alias {
    name                   = aws_cloudfront_distribution.info_openapparel_redirect[0].domain_name
    zone_id                = aws_cloudfront_distribution.info_openapparel_redirect[0].hosted_zone_id
    evaluate_target_health = false
  }
}

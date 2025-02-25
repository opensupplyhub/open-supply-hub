locals {
  frontend_bucket_name = "${lower(replace(var.project, " ", ""))}-${lower(var.environment)}-frontend-${var.aws_region}"
}

resource "aws_s3_bucket" "react" {
  bucket        = local.frontend_bucket_name
  force_destroy = true

  tags = {
    Name        = local.frontend_bucket_name
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
        name = "X-CloudFront-Auth"
        value = var.cloudfront_auth_token
    }
  }

  origin {
    domain_name              = aws_s3_bucket.react.bucket_regional_domain_name
    origin_id                = "originS3"

    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.react.cloudfront_access_identity_path
    }

    custom_header {
        name = "X-CloudFront-Auth"
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
      lambda_arn = "${aws_lambda_function.redirect_to_s3_origin.qualified_arn}"
    }



    compress               = false
    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 0
    max_ttl                = 300
  }

  ordered_cache_behavior {
    path_pattern     = "tile/*"
    allowed_methods = ["GET", "HEAD", "OPTIONS"]
    cached_methods = ["GET", "HEAD", "OPTIONS"]
    target_origin_id = "originAlb"

    forwarded_values {
      query_string = true
      headers = ["Referer"] # To discourage hotlinking to cached tiles

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

  ordered_cache_behavior {
    path_pattern     = "api/*"
    allowed_methods  = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods   = ["GET", "HEAD", "OPTIONS"]
    target_origin_id = "originAlb"

    forwarded_values {
      query_string = true
      headers      = ["*"] # To discourage hotlinking to cached tiles

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
      headers      = ["*"] # To discourage hotlinking to cached tiles

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
      headers      = ["*"] # To discourage hotlinking to cached tiles

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
      headers      = ["*"] # To discourage hotlinking to cached tiles

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
      headers      = ["*"] # To discourage hotlinking to cached tiles

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
      headers      = ["*"] # To discourage hotlinking to cached tiles

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
      headers      = ["*"] # To discourage hotlinking to cached tiles

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
      headers      = ["*"] # To discourage hotlinking to cached tiles

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
      headers      = ["*"] # To discourage hotlinking to cached tiles

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
      headers      = ["*"] # To discourage hotlinking to cached tiles

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
      headers      = ["*"] # To discourage hotlinking to cached tiles

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
      headers      = ["*"] # To discourage hotlinking to cached tiles

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
      headers      = ["*"] # To discourage hotlinking to cached tiles

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
      headers      = ["*"] # To discourage hotlinking to cached tiles

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
      headers      = ["*"] # To discourage hotlinking to cached tiles

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
      headers      = ["*"] # To discourage hotlinking to cached tiles

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
      headers      = ["*"] # To discourage hotlinking to cached tiles

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
      headers      = ["*"] # To discourage hotlinking to cached tiles

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
      headers      = ["*"] # To discourage hotlinking to cached tiles

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
      headers      = ["*"] # To discourage hotlinking to cached tiles

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
      headers      = ["*"] # To discourage hotlinking to cached tiles

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
}

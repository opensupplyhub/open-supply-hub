provider "aws" {
  alias  = "us-east-1"
  region = "us-east-1"
}

resource "aws_wafv2_ip_set" "ip_whitelist" {
  provider           = aws.us-east-1
  name               = "whitelist-ipset"
  description        = "Allowed IPs"
  scope              = "CLOUDFRONT"
  ip_address_version = "IPV4"

  # TODO: move to variables
  addresses = [
    "37.110.160.0/20",
  ]
}

resource "aws_wafv2_web_acl" "web_acl" {
  provider    = aws.us-east-1
  name        = "waf-acl"
  description = "Allow only whitelisted IPs"
  scope       = "CLOUDFRONT"

  default_action {
    block {}
  }

  rule {
    name     = "AllowWhitelistedIPs"
    priority = 0

    action {
      allow {}
    }

    statement {
      ip_set_reference_statement {
        arn = aws_wafv2_ip_set.ip_whitelist.arn
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "AllowWhitelistedIPs"
      sampled_requests_enabled   = true
    }
  }

  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "WebACL"
    sampled_requests_enabled   = true
  }
}

# TODO: switch distribution id to RBA
resource "aws_wafv2_web_acl_association" "dev_association" {
  provider     = aws.us-east-1
  resource_arn = "arn:aws:cloudfront::distribution/${var.cloudfront_distribution_id}"
  web_acl_arn  = aws_wafv2_web_acl.web_acl.arn
}

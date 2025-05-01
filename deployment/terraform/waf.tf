provider "aws" {
  alias  = "us-east-1"
  region = "us-east-1"
}

resource "aws_wafv2_ip_set" "ip_whitelist" {
  # Should be RBA environment in the future
  for_each = var.environment == "Development" ? { dev = "dev" } : {}
  provider           = aws.us-east-1
  name               = "whitelist-ipset"
  description        = "Allowed IPs"
  scope              = "CLOUDFRONT"
  ip_address_version = "IPV4"
  # If no ip addresses in the whitelist, enable traffic for all
  addresses = length(var.ip_whitelist) > 0 ? var.ip_whitelist : ["0.0.0.0/0"]
}

resource "aws_wafv2_web_acl" "web_acl" {
  # Should be RBA environment in the future
  for_each = var.environment == "Development" ? { dev = "dev" } : {}
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
        arn = aws_wafv2_ip_set.ip_whitelist["dev"].arn
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

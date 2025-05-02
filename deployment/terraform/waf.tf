provider "aws" {
  alias  = "us-east-1"
  region = "us-east-1"
}

locals {
  is_whitelist_enabled = length(var.ip_whitelist) > 0
  is_denylist_enabled  = length(var.ip_denylist) > 0

  environment_enabled = toset(["Development", "Production", "Preprod", "Staging", "Test"])
  is_env_enabled      = contains(local.environment_enabled, var.environment)

  web_acl_default_action = local.is_whitelist_enabled ? "block" : "allow"
}

resource "null_resource" "validate_ip_sets" {
  count = (local.is_whitelist_enabled && local.is_denylist_enabled) ? 1 : 0

  provisioner "local-exec" {
    command = "echo 'ERROR: You cannot define both ip_whitelist and ip_denylist at the same time.' && exit 1"
  }
}

resource "aws_wafv2_ip_set" "ip_whitelist" {
  count              = local.is_whitelist_enabled && local.is_env_enabled ? 1 : 0
  provider           = aws.us-east-1
  name               = "whitelist-ipset"
  description        = "Allowed IPs"
  scope              = "CLOUDFRONT"
  ip_address_version = "IPV4"
  addresses          = var.ip_whitelist
}

resource "aws_wafv2_ip_set" "ip_denylist" {
  count              = local.is_denylist_enabled && local.is_env_enabled ? 1 : 0
  provider           = aws.us-east-1
  name               = "denylist-ipset"
  description        = "Blocked IPs"
  scope              = "CLOUDFRONT"
  ip_address_version = "IPV4"
  addresses          = var.ip_denylist
}

resource "aws_wafv2_web_acl" "web_acl" {
  count       = local.is_env_enabled ? 1 : 0
  provider    = aws.us-east-1
  name        = "waf-acl"
  description = "Web ACL for environment ${var.environment}"
  scope       = "CLOUDFRONT"

  dynamic "rule" {
    for_each = local.is_denylist_enabled ? [true] : []
    content {
      name     = "BlockDenylistedIPs"
      priority = 0
      action {
        block {}
      }
      statement {
        ip_set_reference_statement {
          arn = aws_wafv2_ip_set.ip_denylist[0].arn
        }
      }
      visibility_config {
        cloudwatch_metrics_enabled = true
        metric_name                = "BlockDenylistedIPs"
        sampled_requests_enabled   = true
      }
    }
  }

  dynamic "rule" {
    for_each = local.is_whitelist_enabled ? [true] : []
    content {
      name     = "AllowWhitelistedIPs"
      priority = 0
      action {
        allow {}
      }
      statement {
        ip_set_reference_statement {
          arn = aws_wafv2_ip_set.ip_whitelist[0].arn
        }
      }
      visibility_config {
        cloudwatch_metrics_enabled = true
        metric_name                = "AllowWhitelistedIPs"
        sampled_requests_enabled   = true
      }
    }
  }

  dynamic "default_action" {
    for_each = local.is_whitelist_enabled ? [true] : []
    content {
      block {}
    }
  }

  dynamic "default_action" {
    for_each = !local.is_whitelist_enabled ? [true] : []
    content {
      allow {}
    }
  }

  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "WebACL"
    sampled_requests_enabled   = true
  }
}

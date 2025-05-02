provider "aws" {
  alias  = "us-east-1"
  region = "us-east-1"
}

locals {
  is_whitelist_enabled = length(var.ip_whitelist) > 0
  is_denylist_enabled  = length(var.ip_denylist) > 0

  conflicting_lists = local.is_whitelist_enabled && local.is_denylist_enabled

  waf_enabled = local.is_whitelist_enabled || local.is_denylist_enabled
  web_acl_default_action = local.is_whitelist_enabled ? "block" : "allow"

  ip_set_addresses = local.is_whitelist_enabled ? var.ip_whitelist : (
                     local.is_denylist_enabled ? var.ip_denylist : [])

  ip_set_type = local.is_whitelist_enabled ? "whitelist" : (
                local.is_denylist_enabled ? "denylist" : "")
}

resource "null_resource" "validate_ip_lists" {
  count = local.conflicting_lists ? 1 : 0

  provisioner "local-exec" {
    command = "echo 'ERROR: ip_whitelist and ip_denylist cannot both be set' && exit 1"
  }
}

resource "aws_wafv2_ip_set" "ip_whitelist" {
  provider           = aws.us-east-1
  name               = "whitelist-ipset"
  description        = "Allowed IPs"
  scope              = "CLOUDFRONT"
  ip_address_version = "IPV4"
  addresses          = var.ip_whitelist
  depends_on = [aws_wafv2_web_acl.web_acl]
}

resource "aws_wafv2_ip_set" "ip_denylist" {
  provider           = aws.us-east-1
  name               = "denylist-ipset"
  description        = "Blocked IPs"
  scope              = "CLOUDFRONT"
  ip_address_version = "IPV4"
  addresses          = var.ip_denylist
  depends_on = [aws_wafv2_web_acl.web_acl]
}

resource "aws_wafv2_web_acl" "web_acl" {
  for_each = local.waf_enabled ? { (var.environment) = var.environment } : {}
  provider    = aws.us-east-1
  name        = "${var.environment}-web-acl"
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
    metric_name                = "${var.environment}-web-acl-metrics"
    sampled_requests_enabled   = true
  }
}

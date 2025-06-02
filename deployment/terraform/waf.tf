provider "aws" {
  alias  = "us-east-1"
  region = "us-east-1"
}

locals {
  is_whitelist_enabled = length(var.ip_whitelist) > 0
  is_denylist_enabled  = length(var.ip_denylist) > 0
  ip_list_conflict = local.is_whitelist_enabled && local.is_denylist_enabled
  ipv4_whitelist = [
    for ip in var.ip_whitelist :
    ip if can(regex("^([0-9]{1,3}\\.){3}[0-9]{1,3}/[0-9]{1,2}$", ip))
  ]
  ipv6_whitelist = [
    for ip in var.ip_whitelist :
    ip if can(regex(":", ip)) && can(cidrhost(ip, 0))
  ]
  ipv4_denylist = [
    for ip in var.ip_denylist :
    ip if can(regex("^([0-9]{1,3}\\.){3}[0-9]{1,3}/[0-9]{1,2}$", ip))
  ]
  ipv6_denylist = [
    for ip in var.ip_denylist :
    ip if can(regex(":", ip)) && can(cidrhost(ip, 0))
  ]
}

resource "null_resource" "validate_ip_lists" {
  count = local.ip_list_conflict ? 1 : 0

  provisioner "local-exec" {
    command = "echo 'Error: Only one of ip_whitelist or ip_denylist can be defined.' && exit 1"
  }
}

resource "aws_wafv2_ip_set" "ipv4_whitelist" {
  count             = local.is_whitelist_enabled && length(local.ipv4_whitelist) > 0 ? 1 : 0
  provider          = aws.us-east-1
  name              = "${lower(var.environment)}-whitelist-ipv4-ipset"
  description       = "Allowed IPv4 addresses"
  scope             = "CLOUDFRONT"
  ip_address_version = "IPV4"
  addresses         = local.ipv4_whitelist
  tags = { 
    Environment = var.environment
  }
}

resource "aws_wafv2_ip_set" "ipv6_whitelist" {
  count             = local.is_whitelist_enabled && length(local.ipv6_whitelist) > 0 ? 1 : 0
  provider          = aws.us-east-1
  name              = "${lower(var.environment)}-whitelist-ipv6-ipset"
  description       = "Allowed IPv6 addresses"
  scope             = "CLOUDFRONT"
  ip_address_version = "IPV6"
  addresses         = local.ipv6_whitelist
  tags = { 
    Environment = var.environment
  }
}

resource "aws_wafv2_ip_set" "ipv4_denylist" {
  count             = local.is_denylist_enabled && length(local.ipv4_denylist) > 0 ? 1 : 0
  provider          = aws.us-east-1
  name              = "${lower(var.environment)}-denylist-ipv4-ipset"
  description       = "Blocked IPv4 addresses"
  scope             = "CLOUDFRONT"
  ip_address_version = "IPV4"
  addresses         = local.ipv4_denylist
  tags = {
    Environment = var.environment
  }
}

resource "aws_wafv2_ip_set" "ipv6_denylist" {
  count             = local.is_denylist_enabled && length(local.ipv6_denylist) > 0 ? 1 : 0
  provider          = aws.us-east-1
  name              = "${lower(var.environment)}-denylist-ipv6-ipset"
  description       = "Blocked IPv6 addresses"
  scope             = "CLOUDFRONT"
  ip_address_version = "IPV6"
  addresses         = local.ipv6_denylist
  tags = {
    Environment = var.environment
  }
}

resource "aws_wafv2_web_acl" "web_acl" {
  for_each = var.waf_enabled ? { (var.environment) = var.environment } : {}
  provider = aws.us-east-1

  name        = "${var.environment}-web-acl"
  description = "Web ACL for environment ${var.environment}"
  scope       = "CLOUDFRONT"

  dynamic "rule" {
    for_each = local.is_denylist_enabled && length(local.ipv4_denylist) > 0 ? [true] : []
    content {
      name     = "BlockDenylistedIPv4"
      priority = 0
      action {
        block {}
      }
      statement {
        ip_set_reference_statement {
          arn = aws_wafv2_ip_set.ipv4_denylist[0].arn
        }
      }
      visibility_config {
        cloudwatch_metrics_enabled = true
        metric_name                = "BlockDenylistedIPv4"
        sampled_requests_enabled   = true
      }
    }
  }

  dynamic "rule" {
    for_each = local.is_denylist_enabled && length(local.ipv6_denylist) > 0 ? [true] : []
    content {
      name     = "BlockDenylistedIPv6"
      priority = 1
      action {
        block {}
      }
      statement {
        ip_set_reference_statement {
          arn = aws_wafv2_ip_set.ipv6_denylist[0].arn
        }
      }
      visibility_config {
        cloudwatch_metrics_enabled = true
        metric_name                = "BlockDenylistedIPv6"
        sampled_requests_enabled   = true
      }
    }
  }

  dynamic "rule" {
    for_each = local.is_whitelist_enabled && length(local.ipv4_whitelist) > 0 ? [true] : []
    content {
      name     = "AllowWhitelistedIPv4"
      priority = 2
      action {
        allow {}
      }
      statement {
        ip_set_reference_statement {
          arn = aws_wafv2_ip_set.ipv4_whitelist[0].arn
        }
      }
      visibility_config {
        cloudwatch_metrics_enabled = true
        metric_name                = "AllowWhitelistedIPv4"
        sampled_requests_enabled   = true
      }
    }
  }

  dynamic "rule" {
    for_each = local.is_whitelist_enabled && length(local.ipv6_whitelist) > 0 ? [true] : []
    content {
      name     = "AllowWhitelistedIPv6"
      priority = 3
      action {
        allow {}
      }
      statement {
        ip_set_reference_statement {
          arn = aws_wafv2_ip_set.ipv6_whitelist[0].arn
        }
      }
      visibility_config {
        cloudwatch_metrics_enabled = true
        metric_name                = "AllowWhitelistedIPv6"
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
    for_each = local.is_whitelist_enabled ? [] : [true]
    content {
      allow {}
    }
  }

  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "${var.environment}-web-acl-metrics"
    sampled_requests_enabled   = true
  }

  lifecycle {
    create_before_destroy = true
  }
}

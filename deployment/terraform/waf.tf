provider "aws" {
  alias  = "us-east-1"
  region = "us-east-1"
}

locals {
  # Regex patterns for IP validation
  ipv4_cidr_pattern = "^([0-9]{1,3}\\.){3}[0-9]{1,3}/[0-9]{1,2}$"
  ipv6_cidr_pattern = "^([0-9a-fA-F]{1,4}:){1,7}[0-9a-fA-F]{1,4}/[0-9]{1,3}$"

  ipv4_whitelist = [
    for ip in var.ip_whitelist :
    ip if can(regex(local.ipv4_cidr_pattern, ip)) && can(cidrhost(ip, 0))
  ]
  ipv6_whitelist = [
    for ip in var.ip_whitelist :
    ip if can(regex(local.ipv6_cidr_pattern, ip)) && can(cidrhost(ip, 0))
  ]
  ipv4_denylist = [
    for ip in var.ip_denylist :
    ip if can(regex(local.ipv4_cidr_pattern, ip)) && can(cidrhost(ip, 0))
  ]
  ipv6_denylist = [
    for ip in var.ip_denylist :
    ip if can(regex(local.ipv6_cidr_pattern, ip)) && can(cidrhost(ip, 0))
  ]
  is_whitelist_enabled = length(local.ipv4_whitelist) > 0 || length(local.ipv6_whitelist) > 0
  is_denylist_enabled  = length(local.ipv4_denylist)  > 0 || length(local.ipv6_denylist)  > 0
  ip_list_conflict = local.is_whitelist_enabled && local.is_denylist_enabled
  ipset_rules = {
    "BlockDenylistedIPv4" = {
      ip_set      = aws_wafv2_ip_set.ipv4_denylist
      priority    = 0
      action_type = "block"
    }
    "BlockDenylistedIPv6" = {
      ip_set      = aws_wafv2_ip_set.ipv6_denylist
      priority    = 1
      action_type = "block"
    }
    "AllowWhitelistedIPv4" = {
      ip_set      = aws_wafv2_ip_set.ipv4_whitelist
      priority    = 2
      action_type = "allow"
    }
    "AllowWhitelistedIPv6" = {
      ip_set      = aws_wafv2_ip_set.ipv6_whitelist
      priority    = 3
      action_type = "allow"
    }
  }
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
    for_each = {
      for name, cfg in local.ipset_rules : name => cfg
      if length(cfg.ip_set) > 0
    }
    content {
      name     = rule.key
      priority = rule.value.priority

      dynamic "action" {
        for_each = [rule.value.action_type]
        content {
          dynamic "allow" {
            for_each = action.value == "allow" ? [1] : []
            content {}
          }
          dynamic "block" {
            for_each = action.value == "block" ? [1] : []
            content {}
          }
        }
      }
      statement {
        ip_set_reference_statement {
          arn = rule.value.ip_set[0].arn
        }
      }
      visibility_config {
        cloudwatch_metrics_enabled = true
        metric_name                = rule.key
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

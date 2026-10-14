provider "aws" {
  alias  = "us-east-1"
  region = "us-east-1"
}

locals {
  ipv4_cidr_pattern = "^([0-9]{1,3}\\.){3}[0-9]{1,3}/[0-9]{1,2}$"
  ipv6_cidr_pattern = "^[0-9a-fA-F:]+::[0-9a-fA-F:]+/128$"
  ipv4_whitelist = [
    for ip in local.ip_whitelist :
    ip if can(regex(local.ipv4_cidr_pattern, ip)) && can(cidrhost(ip, 0))
  ]
  ipv6_whitelist = [
    for ip in local.ip_whitelist :
    ip if can(cidrhost(ip, 0)) && length(split(".", split("/", ip)[0])) != 4
  ]
  ipv4_denylist = [
    for ip in local.ip_denylist :
    ip if can(regex(local.ipv4_cidr_pattern, ip)) && can(cidrhost(ip, 0))
  ]
  ipv6_denylist = [
    for ip in local.ip_denylist :
    ip if can(cidrhost(ip, 0)) && length(split(".", split("/", ip)[0])) != 4
  ]
  ipv4_rate_limit_exempt = [
    for ip in local.waf_rate_limit_exempt_ips :
    ip if can(regex(local.ipv4_cidr_pattern, ip)) && can(cidrhost(ip, 0))
  ]
  ipv6_rate_limit_exempt = [
    for ip in local.waf_rate_limit_exempt_ips :
    ip if can(cidrhost(ip, 0)) && length(split(".", split("/", ip)[0])) != 4
  ]
  is_whitelist_enabled = length(local.ipv4_whitelist) > 0 || length(local.ipv6_whitelist) > 0
  is_denylist_enabled  = length(local.ipv4_denylist) > 0 || length(local.ipv6_denylist) > 0
  ip_list_conflict     = local.is_whitelist_enabled && local.is_denylist_enabled
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

  # OSDEV-2138: infrastructure-level rate limiting for the API.
  # Requests from rate-limit-exempt IPs get this label (count action, so
  # evaluation continues) and the rate-based rules below skip them.
  rate_limit_exempt_label = "osh:rate-limit:exempt"
  rate_limit_exempt_rules = {
    "LabelRateLimitExemptIPv4" = {
      ip_set   = aws_wafv2_ip_set.ipv4_rate_limit_exempt
      priority = 10
    }
    "LabelRateLimitExemptIPv6" = {
      ip_set   = aws_wafv2_ip_set.ipv6_rate_limit_exempt
      priority = 11
    }
  }
  # Both rules count every request whose path starts with /api/ per
  # source IP, over var.waf_rate_limit_evaluation_window_sec.
  # ApiRateLimitAnonPerIp only counts requests without an API token
  # ("Authorization: Token ..."): the web app, browser sessions and
  # scripts using the web client path.
  rate_limit_rules = {
    "ApiRateLimitPerIp" = {
      priority          = 20
      limit             = var.waf_api_rate_limit_per_ip
      only_without_auth = false
    }
    "ApiRateLimitAnonPerIp" = {
      priority          = 21
      limit             = var.waf_api_anon_rate_limit_per_ip
      only_without_auth = true
    }
  }
  rate_limit_response_body_key = "rate-limited"
}

resource "null_resource" "validate_ip_lists" {
  count = local.ip_list_conflict ? 1 : 0

  provisioner "local-exec" {
    command = "echo 'Error: Only one of ip_whitelist or ip_denylist can be defined.' && exit 1"
  }
}

resource "aws_wafv2_ip_set" "ipv4_whitelist" {
  count              = local.is_whitelist_enabled && length(local.ipv4_whitelist) > 0 ? 1 : 0
  provider           = aws.us-east-1
  name               = "${lower(var.environment)}-whitelist-ipv4-ipset"
  description        = "Allowed IPv4 addresses"
  scope              = "CLOUDFRONT"
  ip_address_version = "IPV4"
  addresses          = local.ipv4_whitelist
  tags = {
    Environment = var.environment
  }
}

resource "aws_wafv2_ip_set" "ipv6_whitelist" {
  count              = local.is_whitelist_enabled && length(local.ipv6_whitelist) > 0 ? 1 : 0
  provider           = aws.us-east-1
  name               = "${lower(var.environment)}-whitelist-ipv6-ipset"
  description        = "Allowed IPv6 addresses"
  scope              = "CLOUDFRONT"
  ip_address_version = "IPV6"
  addresses          = local.ipv6_whitelist
  tags = {
    Environment = var.environment
  }
}

resource "aws_wafv2_ip_set" "ipv4_denylist" {
  count              = local.is_denylist_enabled && length(local.ipv4_denylist) > 0 ? 1 : 0
  provider           = aws.us-east-1
  name               = "${lower(var.environment)}-denylist-ipv4-ipset"
  description        = "Blocked IPv4 addresses"
  scope              = "CLOUDFRONT"
  ip_address_version = "IPV4"
  addresses          = local.ipv4_denylist
  tags = {
    Environment = var.environment
  }
}

resource "aws_wafv2_ip_set" "ipv6_denylist" {
  count              = local.is_denylist_enabled && length(local.ipv6_denylist) > 0 ? 1 : 0
  provider           = aws.us-east-1
  name               = "${lower(var.environment)}-denylist-ipv6-ipset"
  description        = "Blocked IPv6 addresses"
  scope              = "CLOUDFRONT"
  ip_address_version = "IPV6"
  addresses          = local.ipv6_denylist
  tags = {
    Environment = var.environment
  }
}

resource "aws_wafv2_ip_set" "ipv4_rate_limit_exempt" {
  count              = length(local.ipv4_rate_limit_exempt) > 0 ? 1 : 0
  provider           = aws.us-east-1
  name               = "${lower(var.environment)}-rate-limit-exempt-ipv4-ipset"
  description        = "IPv4 addresses exempt from the API rate-based rules"
  scope              = "CLOUDFRONT"
  ip_address_version = "IPV4"
  addresses          = local.ipv4_rate_limit_exempt
  tags = {
    Environment = var.environment
  }
}

resource "aws_wafv2_ip_set" "ipv6_rate_limit_exempt" {
  count              = length(local.ipv6_rate_limit_exempt) > 0 ? 1 : 0
  provider           = aws.us-east-1
  name               = "${lower(var.environment)}-rate-limit-exempt-ipv6-ipset"
  description        = "IPv6 addresses exempt from the API rate-based rules"
  scope              = "CLOUDFRONT"
  ip_address_version = "IPV6"
  addresses          = local.ipv6_rate_limit_exempt
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

  dynamic "rule" {
    for_each = {
      for name, cfg in local.rate_limit_exempt_rules : name => cfg
      if var.waf_rate_limit_enabled && length(cfg.ip_set) > 0
    }
    content {
      name     = rule.key
      priority = rule.value.priority

      action {
        count {}
      }

      rule_label {
        name = local.rate_limit_exempt_label
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

  dynamic "rule" {
    for_each = var.waf_rate_limit_enabled ? local.rate_limit_rules : {}
    content {
      name     = rule.key
      priority = rule.value.priority

      action {
        dynamic "count" {
          for_each = var.waf_rate_limit_action == "count" ? [1] : []
          content {}
        }
        dynamic "block" {
          for_each = var.waf_rate_limit_action == "block" ? [1] : []
          content {
            custom_response {
              response_code            = 429
              custom_response_body_key = local.rate_limit_response_body_key
            }
          }
        }
      }

      statement {
        rate_based_statement {
          limit                 = rule.value.limit
          aggregate_key_type    = "IP"
          evaluation_window_sec = var.waf_rate_limit_evaluation_window_sec

          scope_down_statement {
            and_statement {
              # Path starts with /api/
              statement {
                byte_match_statement {
                  search_string         = "/api/"
                  positional_constraint = "STARTS_WITH"
                  field_to_match {
                    uri_path {}
                  }
                  text_transformation {
                    priority = 0
                    type     = "URL_DECODE"
                  }
                  text_transformation {
                    priority = 1
                    type     = "LOWERCASE"
                  }
                }
              }

              # Not from a rate-limit-exempt IP
              statement {
                not_statement {
                  statement {
                    label_match_statement {
                      scope = "LABEL"
                      key   = local.rate_limit_exempt_label
                    }
                  }
                }
              }

              # Anonymous rule only: no "Authorization: Token ..." header
              dynamic "statement" {
                for_each = rule.value.only_without_auth ? [1] : []
                content {
                  not_statement {
                    statement {
                      byte_match_statement {
                        search_string         = "token "
                        positional_constraint = "STARTS_WITH"
                        field_to_match {
                          single_header {
                            name = "authorization"
                          }
                        }
                        text_transformation {
                          priority = 0
                          type     = "LOWERCASE"
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }

      visibility_config {
        cloudwatch_metrics_enabled = true
        metric_name                = rule.key
        sampled_requests_enabled   = true
      }
    }
  }

  # Same shape as the 429 Django REST Framework returns when it throttles,
  # so API clients that already handle Django's 429s keep working.
  custom_response_body {
    key          = local.rate_limit_response_body_key
    content      = jsonencode({ detail = "Request was throttled." })
    content_type = "APPLICATION_JSON"
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

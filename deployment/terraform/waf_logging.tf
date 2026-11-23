#
# OSDEV-3614: AWS WAF logging for the web ACL in waf.tf.
#
# Only requests that a rule COUNTED or BLOCKED are kept (logging_filter below),
# so the volume stays small: today that is the API rate-based rules while they
# run in Count mode, plus denylist blocks. Once the rate rules move to Block,
# their blocks are logged too, which answers "why was this client blocked?".
#
# Constraints:
#   * A CloudFront-scoped web ACL can only log to a CloudWatch Logs log group
#     in us-east-1, and the log group name must start with "aws-waf-logs-".
#   * The log group needs a resource policy that lets the log delivery service
#     write into it. One policy per environment, named per environment, like
#     route53_query_logging.tf (CloudWatch Logs allows 10 per region/account).
#   * Authorization, Cookie and X-OAR-CLIENT-KEY values are redacted, so API
#     tokens, sessions and the web client key never land in the logs. The
#     header names stay, so we can still tell token requests apart.
#
# Find matched IPs with CloudWatch Logs Insights on the log group, e.g.:
#   fields httpRequest.clientIp as ip
#   | filter nonTerminatingMatchingRules.0.ruleId like /ApiRateLimit/
#       or terminatingRuleId like /ApiRateLimit/
#   | stats count(*) as matched by ip
#   | sort matched desc
#

locals {
  waf_logging_enabled = var.waf_enabled && var.waf_logging_enabled
  waf_log_group_name  = "aws-waf-logs-${lower(replace(var.project, " ", ""))}-${lower(var.environment)}"
}

resource "aws_cloudwatch_log_group" "waf" {
  provider = aws.us-east-1
  count    = local.waf_logging_enabled ? 1 : 0

  name              = local.waf_log_group_name
  retention_in_days = var.waf_log_retention_days

  tags = {
    Name        = local.waf_log_group_name
    Project     = var.project
    Environment = var.environment
  }
}

data "aws_iam_policy_document" "waf_logging" {
  count = local.waf_logging_enabled ? 1 : 0

  statement {
    sid    = "WafLogsDelivery"
    effect = "Allow"

    actions = [
      "logs:CreateLogStream",
      "logs:PutLogEvents",
    ]

    principals {
      type        = "Service"
      identifiers = ["delivery.logs.amazonaws.com"]
    }

    resources = ["${aws_cloudwatch_log_group.waf[0].arn}:*"]

    # Guards against the confused deputy problem: only our own account's
    # log deliveries may write into this log group.
    condition {
      test     = "StringEquals"
      variable = "aws:SourceAccount"
      values   = [data.aws_caller_identity.current.account_id]
    }

    condition {
      test     = "ArnLike"
      variable = "aws:SourceArn"
      values   = ["arn:aws:logs:us-east-1:${data.aws_caller_identity.current.account_id}:*"]
    }
  }
}

resource "aws_cloudwatch_log_resource_policy" "waf_logging" {
  provider = aws.us-east-1
  count    = local.waf_logging_enabled ? 1 : 0

  policy_name     = "${lower(replace(var.project, " ", ""))}-${lower(var.environment)}-waf-logging"
  policy_document = data.aws_iam_policy_document.waf_logging[0].json
}

resource "aws_wafv2_web_acl_logging_configuration" "web_acl" {
  provider = aws.us-east-1
  count    = local.waf_logging_enabled ? 1 : 0

  resource_arn            = aws_wafv2_web_acl.web_acl[var.environment].arn
  log_destination_configs = [aws_cloudwatch_log_group.waf[0].arn]

  redacted_fields {
    single_header {
      name = "authorization"
    }
  }

  redacted_fields {
    single_header {
      name = "cookie"
    }
  }

  redacted_fields {
    single_header {
      name = "x-oar-client-key"
    }
  }

  logging_filter {
    default_behavior = "DROP"

    filter {
      behavior    = "KEEP"
      requirement = "MEETS_ANY"

      condition {
        action_condition {
          action = "COUNT"
        }
      }

      condition {
        action_condition {
          action = "BLOCK"
        }
      }
    }
  }

  depends_on = [aws_cloudwatch_log_resource_policy.waf_logging]
}

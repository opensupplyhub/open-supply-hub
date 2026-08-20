resource "aws_sns_topic" "global" {
  name = "topic${local.short}GlobalNotifications"
}

# aws_sns_topic.global otherwise relies on SNS's implicit default policy,
# which only covers principals in the owner account. AWS Budgets publishes
# as a service principal, so it needs an explicit grant; the first
# statement restates the default owner-account access so attaching this
# policy does not narrow what already works (CloudWatch alarms, Chatbot
# subscriptions).
data "aws_iam_policy_document" "global_topic" {
  statement {
    sid    = "DefaultSNSTopicOwnerAccess"
    effect = "Allow"

    principals {
      type        = "AWS"
      identifiers = ["*"]
    }

    actions = [
      "SNS:GetTopicAttributes",
      "SNS:SetTopicAttributes",
      "SNS:AddPermission",
      "SNS:RemovePermission",
      "SNS:DeleteTopic",
      "SNS:Subscribe",
      "SNS:ListSubscriptionsByTopic",
      "SNS:Publish",
    ]

    resources = [aws_sns_topic.global.arn]

    condition {
      test     = "StringEquals"
      variable = "AWS:SourceOwner"
      values   = [data.aws_caller_identity.current.account_id]
    }
  }

  statement {
    sid    = "AllowBudgetsPublish"
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["budgets.amazonaws.com"]
    }

    actions   = ["SNS:Publish"]
    resources = [aws_sns_topic.global.arn]

    condition {
      test     = "StringEquals"
      variable = "aws:SourceAccount"
      values   = [data.aws_caller_identity.current.account_id]
    }
  }
}

resource "aws_sns_topic_policy" "global" {
  arn    = aws_sns_topic.global.arn
  policy = data.aws_iam_policy_document.global_topic.json
}

# Catches runaway Bedrock usage (a frontend retry loop, scripted
# submissions) that per-user API throttles bound in rate but not in
# volume; there is deliberately no in-app cap. The SLC submission-quality
# check is the only Bedrock caller today and its organic volume is a
# handful of calls per day, so the threshold sits orders of magnitude
# above real traffic while still firing within the first hour of a
# runaway. No ModelId dimension, so future models and callers are covered
# too. Bedrock metrics land in the calling region: this alarm only sees
# traffic when the app's BEDROCK_AWS_REGION matches this environment's
# aws_region. Zero calls in an hour is the normal state, hence
# notBreaching on missing data (and no insufficient-data notifications).
resource "aws_cloudwatch_metric_alarm" "bedrock_invocations" {
  alarm_name          = "alarm${local.short}BedrockInvocations"
  alarm_description   = "Unusually high Bedrock model invocation volume"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "Invocations"
  namespace           = "AWS/Bedrock"
  period              = "3600"
  statistic           = "Sum"
  treat_missing_data  = "notBreaching"

  threshold = var.bedrock_invocations_alarm_hourly_threshold

  alarm_actions = [aws_sns_topic.global.arn]
  ok_actions    = [aws_sns_topic.global.arn]
}

# Account-level backstop on Bedrock spend, alerting through the same
# SNS topic -> Chatbot -> Slack path as the CloudWatch alarms. Budgets
# are account-wide, so exactly one environment per AWS account creates
# this (var.manage_bedrock_cost_budget, same ownership pattern as the
# Chatbot channel configuration). The Service cost filter name comes
# from Cost Explorer; if Bedrock spend ever shows up there under an
# additional service name (e.g. a marketplace-listed model), add it to
# the values list.
resource "aws_budgets_budget" "bedrock" {
  count = var.manage_bedrock_cost_budget ? 1 : 0

  name         = "budget${local.short}Bedrock"
  budget_type  = "COST"
  limit_amount = var.bedrock_cost_budget_monthly_limit_usd
  limit_unit   = "USD"
  time_unit    = "MONTHLY"

  cost_filter {
    name   = "Service"
    values = ["Amazon Bedrock"]
  }

  notification {
    comparison_operator       = "GREATER_THAN"
    threshold                 = 80
    threshold_type            = "PERCENTAGE"
    notification_type         = "ACTUAL"
    subscriber_sns_topic_arns = [aws_sns_topic.global.arn]
  }

  notification {
    comparison_operator       = "GREATER_THAN"
    threshold                 = 100
    threshold_type            = "PERCENTAGE"
    notification_type         = "FORECASTED"
    subscriber_sns_topic_arns = [aws_sns_topic.global.arn]
  }
}

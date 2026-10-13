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

# The SLC submission quality check fails open by design: any Bedrock
# error is logged and the submission proceeds with no warning shown, so
# an outage is invisible to contributors and moderators alike (this
# happened Aug 28-31 2026, when the production account lacked the AWS
# Marketplace subscription for the model - OSDEV-3369). The filter
# pattern must match the message logged by evaluate() in
# src/django/api/services/submission_quality_service.py; update both
# together. Namespaced by environment because Production, Staging, and
# RBA share an AWS account.
resource "aws_cloudwatch_log_metric_filter" "submission_quality_check_failures" {
  name           = "filter${local.short}SubmissionQualityCheckFailures"
  log_group_name = aws_cloudwatch_log_group.app.name
  pattern        = "\"Submission quality check failed\""

  metric_transformation {
    name          = "SubmissionQualityCheckFailures"
    namespace     = local.short
    value         = "1"
    default_value = "0"
  }
}

# Any single fail-open occurrence alarms: organic SLC volume is low
# enough that even one silent failure is worth a look, and a systemic
# cause (revoked model access, IAM drift, a deprecated model ID) fails
# every call, so the first failure is usually the start of an outage.
# Zero failures is the normal state, hence notBreaching on missing data.
resource "aws_cloudwatch_metric_alarm" "submission_quality_check_failures" {
  alarm_name          = "alarm${local.short}SubmissionQualityCheckFailures"
  alarm_description   = "SLC submission quality check is failing open (submissions skip the LLM data-quality warnings)"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = aws_cloudwatch_log_metric_filter.submission_quality_check_failures.metric_transformation[0].name
  namespace           = aws_cloudwatch_log_metric_filter.submission_quality_check_failures.metric_transformation[0].namespace
  period              = "3600"
  statistic           = "Sum"
  threshold           = "0"
  treat_missing_data  = "notBreaching"

  alarm_actions = [aws_sns_topic.global.arn]
  ok_actions    = [aws_sns_topic.global.arn]
}

# Catches errors from every Lambda function in this region - the ContriBot
# pipeline (fetch/process/notify/retry), the Batch and Step Functions
# alerting functions, and the private-link NLB registrar - plus any
# function added later. Deliberately un-dimensioned: no FunctionName, so
# new functions are covered the moment they are created and no alarm has
# to be added alongside them. The trade-off is that Slack says "some
# Lambda errored", not which one; the AWS/Lambda Errors metric broken down
# by FunctionName, or the function's log group, identifies it in triage.
#
# Sum over 300s with a threshold of 0 means any single error pages. Lambda
# errors here are not routine - the alerting functions fire on Batch/SFN
# failures and the ContriBot steps handle their own retries - so a raised
# error count is a real signal. If an environment proves noisy, raise
# lambda_errors_alarm_threshold in its tfvars rather than dropping the alarm.
#
# treat_missing_data = notBreaching: an idle environment publishes no
# datapoints at all, which is the normal state, so missing data must not
# page (and no insufficient-data notifications, matching the Bedrock alarm).
#
# Scope note: this alarm lives in the environment's own region. The two
# Lambda@Edge functions (RedirectToS3origin, AddSecurityHeaders) publish
# their AWS/Lambda metrics into the region closest to where CloudFront ran
# them, so they are covered here only for edge executions that land in
# var.aws_region. See doc/ops/monitoring.md for the residual gap.
resource "aws_cloudwatch_metric_alarm" "lambda_errors" {
  alarm_name          = "alarm${local.short}LambdaErrors"
  alarm_description   = "Errors reported by any Lambda function in this region"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = "300"
  statistic           = "Sum"
  treat_missing_data  = "notBreaching"

  threshold = var.lambda_errors_alarm_threshold

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

# ---------------------------------------------------------------------------
# Identity resolver (OSDEV-3587)
#
# The resolver is public and unauthenticated, so it is the one endpoint in
# this project a stranger can drive without an account. Django-level
# throttling is the only limiter: waf.tf carries IP allow and deny lists but
# no rate-based statements. That is the same position as every other public
# endpoint here, so it is not new exposure, but it is worth stating rather
# than assuming.
#
# Nothing alarms on 404 or 400 from /osid/. Both are ordinary answers: a 404
# means the identifier is not resolvable on this instance, which is the
# documented response for an identifier issued elsewhere, and a 400 means
# somebody pasted a typo. Alarming on either would page on correct behaviour.
# ---------------------------------------------------------------------------

resource "aws_cloudwatch_log_metric_filter" "resolver_server_errors" {
  name           = "filter${local.short}ResolverServerErrors"
  log_group_name = aws_cloudwatch_log_group.app.name
  pattern        = "\"Internal Server Error: /osid/\""

  metric_transformation {
    name          = "ResolverServerErrors"
    namespace     = local.short
    value         = "1"
    default_value = "0"
  }
}

# Any single occurrence alarms. A 500 from the resolver should be
# impossible: a malformed identifier is rejected before any lookup, an
# unknown one returns 404, and an unreachable issuer is handled by the
# retrieval service rather than raised. So one error means something is
# wrong that we have not modelled, and this endpoint is the public face of
# the pilot.
resource "aws_cloudwatch_metric_alarm" "resolver_server_errors" {
  alarm_name          = "alarm${local.short}ResolverServerErrors"
  alarm_description   = "The identity resolver is returning server errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = aws_cloudwatch_log_metric_filter.resolver_server_errors.metric_transformation[0].name
  namespace           = aws_cloudwatch_log_metric_filter.resolver_server_errors.metric_transformation[0].namespace
  period              = "3600"
  statistic           = "Sum"
  threshold           = "0"
  treat_missing_data  = "notBreaching"

  alarm_actions = [aws_sns_topic.global.arn]
  ok_actions    = [aws_sns_topic.global.arn]
}

resource "aws_cloudwatch_log_metric_filter" "resolver_throttled" {
  name           = "filter${local.short}ResolverThrottled"
  log_group_name = aws_cloudwatch_log_group.app.name
  pattern        = "\"Too Many Requests: /osid/\""

  metric_transformation {
    name          = "ResolverThrottled"
    namespace     = local.short
    value         = "1"
    default_value = "0"
  }
}

# Deliberately not zero. Occasional throttling is the limiter working, and
# one caller behind a corporate address can reach the burst rate
# legitimately. Sustained throttling is the signal: either somebody is
# hammering the endpoint, or a real integrator needs a higher allowance and
# is currently being refused. Both are worth a look, neither is an outage.
resource "aws_cloudwatch_metric_alarm" "resolver_throttled" {
  alarm_name          = "alarm${local.short}ResolverThrottled"
  alarm_description   = "The identity resolver is throttling sustained traffic from one or more callers"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = aws_cloudwatch_log_metric_filter.resolver_throttled.metric_transformation[0].name
  namespace           = aws_cloudwatch_log_metric_filter.resolver_throttled.metric_transformation[0].namespace
  period              = "3600"
  statistic           = "Sum"
  threshold           = var.resolver_throttled_alarm_threshold
  treat_missing_data  = "notBreaching"

  alarm_actions = [aws_sns_topic.global.arn]
  ok_actions    = [aws_sns_topic.global.arn]
}

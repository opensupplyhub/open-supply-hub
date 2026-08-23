#
# AWS Chatbot → Slack for CloudWatch alarms on aws_sns_topic.global.
# See doc/ops/monitoring.md for Slack setup and shared-account ownership.
#
# AWS allows only one Slack channel configuration per channel per account.
# When multiple envs share an account + channel, one env owns the config
# (aws_chatbot_manage_channel_configuration = true) and lists sibling SNS
# topic ARNs in aws_chatbot_additional_sns_topic_arns; siblings set manage = false.
#

data "aws_iam_policy_document" "chatbot_assume_role" {
  count = var.aws_chatbot_manage_channel_configuration ? 1 : 0

  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["chatbot.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "chatbot" {
  count = var.aws_chatbot_manage_channel_configuration ? 1 : 0

  name               = "role${local.short}Chatbot"
  assume_role_policy = data.aws_iam_policy_document.chatbot_assume_role[0].json

  tags = merge(local.default_tags, {
    Name = "role${local.short}Chatbot"
  })
}

# Allows Chatbot to enrich Slack messages with CloudWatch alarm details / graphs.
resource "aws_iam_role_policy_attachment" "chatbot_cloudwatch_readonly" {
  count = var.aws_chatbot_manage_channel_configuration ? 1 : 0

  role       = aws_iam_role.chatbot[0].name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchReadOnlyAccess"
}

resource "aws_chatbot_slack_channel_configuration" "global_alarms" {
  count = var.aws_chatbot_manage_channel_configuration ? 1 : 0

  configuration_name = "chatbot${local.short}GlobalAlarms"
  iam_role_arn       = aws_iam_role.chatbot[0].arn
  slack_team_id      = local.aws_chatbot_slack_config.team_id
  slack_channel_id   = local.aws_chatbot_slack_config.channel_id
  logging_level      = "ERROR"

  sns_topic_arns = concat(
    [aws_sns_topic.global.arn],
    local.aws_chatbot_additional_sns_topic_arns,
  )

  # Constrain actions Chatbot can take from Slack (notify-only use case).
  guardrail_policy_arns = [
    "arn:aws:iam::aws:policy/ReadOnlyAccess",
  ]

  tags = merge(local.default_tags, {
    Name = "chatbot${local.short}GlobalAlarms"
  })
}

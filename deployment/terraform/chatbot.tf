#
# AWS Chatbot → Slack for CloudWatch alarms on aws_sns_topic.global.
# See doc/ops/monitoring.md for Slack setup. Empty team/channel IDs skip create.
#

locals {
  aws_chatbot_enabled = (
    var.aws_chatbot_slack_team_id != "" &&
    var.aws_chatbot_slack_channel_id != ""
  )
}

data "aws_iam_policy_document" "chatbot_assume_role" {
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
  count = local.aws_chatbot_enabled ? 1 : 0

  name               = "role${local.short}Chatbot"
  assume_role_policy = data.aws_iam_policy_document.chatbot_assume_role.json

  tags = merge(local.default_tags, {
    Name = "role${local.short}Chatbot"
  })
}

# Allows Chatbot to enrich Slack messages with CloudWatch alarm details / graphs.
resource "aws_iam_role_policy_attachment" "chatbot_cloudwatch_readonly" {
  count = local.aws_chatbot_enabled ? 1 : 0

  role       = aws_iam_role.chatbot[0].name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchReadOnlyAccess"
}

resource "aws_chatbot_slack_channel_configuration" "global_alarms" {
  count = local.aws_chatbot_enabled ? 1 : 0

  configuration_name = "chatbot${local.short}GlobalAlarms"
  iam_role_arn       = aws_iam_role.chatbot[0].arn
  slack_team_id      = var.aws_chatbot_slack_team_id
  slack_channel_id   = var.aws_chatbot_slack_channel_id
  logging_level      = "ERROR"

  sns_topic_arns = [
    aws_sns_topic.global.arn,
  ]

  # Constrain actions Chatbot can take from Slack (notify-only use case).
  guardrail_policy_arns = [
    "arn:aws:iam::aws:policy/ReadOnlyAccess",
  ]

  tags = merge(local.default_tags, {
    Name = "chatbot${local.short}GlobalAlarms"
  })
}

#
# ContriBot Step Functions
#

data "template_file" "contribot_state_machine" {
  template = file("${path.module}/step-functions/contribot.json")

  vars = {
    fetch_lists_lambda_arn  = aws_lambda_function.contribot_fetch_lists.arn
    process_list_lambda_arn = aws_lambda_function.contribot_process_list.arn
    notify_lambda_arn       = aws_lambda_function.contribot_notify.arn
  }
}

data "aws_iam_policy_document" "contribot_step_functions" {
  statement {
    effect = "Allow"

    actions = [
      "lambda:InvokeFunction",
    ]

    resources = [
      aws_lambda_function.contribot_fetch_lists.arn,
      aws_lambda_function.contribot_process_list.arn,
      aws_lambda_function.contribot_notify.arn,
    ]
  }
}

resource "aws_iam_role" "contribot_step_functions" {
  name               = "stepFunctions${local.short}Contribot"
  assume_role_policy = data.aws_iam_policy_document.step_functions_assume_role.json

  tags = merge(local.default_tags, {
    Name = "stepFunctionsContribot"
  })
}

resource "aws_iam_role_policy" "contribot_step_functions" {
  name = "stepFunctions${local.short}ContribotPolicy"
  role = aws_iam_role.contribot_step_functions.id

  policy = data.aws_iam_policy_document.contribot_step_functions.json
}

resource "aws_sfn_state_machine" "contribot" {
  name     = "stateMachine${local.short}Contribot"
  role_arn = aws_iam_role.contribot_step_functions.arn

  definition = data.template_file.contribot_state_machine.rendered

  tags = merge(local.default_tags, {
    Name = "stateMachineContribot"
  })
}

resource "aws_lambda_permission" "contribot_fetch_lists_sfn" {
  statement_id  = "perm${local.short}ContribotFetchListsStepFunctions"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.contribot_fetch_lists.function_name
  principal     = "states.amazonaws.com"
  source_arn    = aws_sfn_state_machine.contribot.arn
}

resource "aws_lambda_permission" "contribot_process_list_sfn" {
  statement_id  = "perm${local.short}ContribotProcessListStepFunctions"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.contribot_process_list.function_name
  principal     = "states.amazonaws.com"
  source_arn    = aws_sfn_state_machine.contribot.arn
}

resource "aws_lambda_permission" "contribot_notify_sfn" {
  statement_id  = "perm${local.short}ContribotNotifyStepFunctions"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.contribot_notify.function_name
  principal     = "states.amazonaws.com"
  source_arn    = aws_sfn_state_machine.contribot.arn
}

#
# ContriBot schedule
#

data "aws_iam_policy_document" "contribot_cloudwatch_events" {
  statement {
    effect = "Allow"

    resources = [aws_sfn_state_machine.contribot.arn]

    actions = ["states:StartExecution"]
  }
}

resource "aws_iam_role" "contribot_cloudwatch_events" {
  name               = "cloudWatchEvents${local.short}Contribot"
  assume_role_policy = data.aws_iam_policy_document.cloudwatch_events_assume_role.json

  tags = merge(local.default_tags, {
    Name = "cloudWatchEventsContribot"
  })
}

resource "aws_iam_role_policy" "contribot_cloudwatch_events" {
  name = "cloudWatchEvents${local.short}ContribotPolicy"
  role = aws_iam_role.contribot_cloudwatch_events.id

  policy = data.aws_iam_policy_document.contribot_cloudwatch_events.json
}

resource "aws_cloudwatch_event_rule" "contribot" {
  name                = "eventRule${local.short}Contribot"
  description         = "Run ContriBot workflow on schedule (${var.contribot_schedule_expression})"
  schedule_expression = var.contribot_schedule_expression

  tags = merge(local.default_tags, {
    Name = "eventRuleContribot"
  })
}

resource "aws_cloudwatch_event_target" "contribot" {
  target_id = "eventTarget${local.short}Contribot"
  rule      = aws_cloudwatch_event_rule.contribot.name
  arn       = aws_sfn_state_machine.contribot.arn
  role_arn  = aws_iam_role.contribot_cloudwatch_events.arn
}

#
# ContriBot Lambda functions
#

locals {
  contribot_lambda_environment = {
    ENVIRONMENT                         = var.environment
    CONTRIBOT_STATE_TABLE_NAME          = aws_dynamodb_table.contribot_state.name
    AWS_STORAGE_BUCKET_NAME             = local.files_bucket_name
    OS_HUB_API_URL                      = "https://${var.r53_public_hosted_zone}"
    MONDAY_API_URL                      = "https://api.monday.com/v2"
    MONDAY_BOARD_ID                     = var.contribot_monday_board_id
    GOOGLE_DRIVE_SHARED_DIRECTORY_ID    = var.contribot_google_drive_shared_directory_id
    OS_HUB_API_TOKEN_SECRET_ARN         = aws_secretsmanager_secret.contribot_os_hub_api_token.arn
    MONDAY_API_KEY_SECRET_ARN           = aws_secretsmanager_secret.contribot_monday_api_key.arn
    SLACK_API_URL_SECRET_ARN            = aws_secretsmanager_secret.contribot_slack_api_url.arn
    GOOGLE_DRIVE_SERVICE_KEY_SECRET_ARN = aws_secretsmanager_secret.contribot_google_drive_service_key.arn
  }
}

data "aws_iam_policy_document" "contribot_lambda" {
  statement {
    effect = "Allow"

    actions = [
      "dynamodb:GetItem",
      "dynamodb:PutItem",
      "dynamodb:UpdateItem",
      "dynamodb:Query",
      "dynamodb:Scan",
    ]

    resources = [aws_dynamodb_table.contribot_state.arn]
  }

  statement {
    effect = "Allow"

    actions = [
      "secretsmanager:GetSecretValue",
    ]

    resources = [
      aws_secretsmanager_secret.contribot_os_hub_api_token.arn,
      aws_secretsmanager_secret.contribot_monday_api_key.arn,
      aws_secretsmanager_secret.contribot_slack_api_url.arn,
      aws_secretsmanager_secret.contribot_google_drive_service_key.arn,
    ]
  }

  statement {
    effect = "Allow"

    actions = [
      "s3:GetObject",
    ]

    resources = ["${aws_s3_bucket.files.arn}/*"]
  }
}

resource "aws_iam_role" "contribot_lambda" {
  name               = "lambda${local.short}Contribot"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json

  tags = merge(local.default_tags, {
    Name = "lambdaContribot"
  })
}

resource "aws_iam_role_policy_attachment" "contribot_lambda_basic_execution" {
  role       = aws_iam_role.contribot_lambda.name
  policy_arn = var.aws_lambda_service_role_policy_arn
}

resource "aws_iam_role_policy" "contribot_lambda" {
  name = "lambda${local.short}ContribotPolicy"
  role = aws_iam_role.contribot_lambda.id

  policy = data.aws_iam_policy_document.contribot_lambda.json
}

resource "aws_cloudwatch_log_group" "contribot_fetch_lists" {
  name              = "/aws/lambda/func${local.short}ContribotFetchLists"
  retention_in_days = 365

  tags = merge(local.default_tags, {
    Name = "logContribotFetchLists"
  })
}

resource "aws_cloudwatch_log_group" "contribot_process_list" {
  name              = "/aws/lambda/func${local.short}ContribotProcessList"
  retention_in_days = 365

  tags = merge(local.default_tags, {
    Name = "logContribotProcessList"
  })
}

resource "aws_cloudwatch_log_group" "contribot_notify" {
  name              = "/aws/lambda/func${local.short}ContribotNotify"
  retention_in_days = 365

  tags = merge(local.default_tags, {
    Name = "logContribotNotify"
  })
}

resource "aws_lambda_function" "contribot_fetch_lists" {
  filename         = "${path.module}/lambda-functions/contribot_fetch_lists/contribot_fetch_lists.zip"
  source_code_hash = filebase64sha256("${path.module}/lambda-functions/contribot_fetch_lists/contribot_fetch_lists.zip")
  function_name    = "func${local.short}ContribotFetchLists"
  description      = "ContriBot task that fetches newly processed facility lists."
  role             = aws_iam_role.contribot_lambda.arn
  handler          = "handler.handler"
  runtime          = "python3.10"
  timeout          = 60
  memory_size      = 256

  environment {
    variables = local.contribot_lambda_environment
  }

  depends_on = [
    aws_cloudwatch_log_group.contribot_fetch_lists,
    aws_iam_role_policy_attachment.contribot_lambda_basic_execution,
  ]

  tags = merge(local.default_tags, {
    Name = "funcContribotFetchLists"
  })
}

resource "aws_lambda_function" "contribot_process_list" {
  filename         = "${path.module}/lambda-functions/contribot_process_list/contribot_process_list.zip"
  source_code_hash = filebase64sha256("${path.module}/lambda-functions/contribot_process_list/contribot_process_list.zip")
  function_name    = "func${local.short}ContribotProcessList"
  description      = "ContriBot task that processes a single facility list."
  role             = aws_iam_role.contribot_lambda.arn
  handler          = "handler.handler"
  runtime          = "python3.10"
  timeout          = 300
  memory_size      = 512

  environment {
    variables = local.contribot_lambda_environment
  }

  depends_on = [
    aws_cloudwatch_log_group.contribot_process_list,
    aws_iam_role_policy_attachment.contribot_lambda_basic_execution,
  ]

  tags = merge(local.default_tags, {
    Name = "funcContribotProcessList"
  })
}

resource "aws_lambda_function" "contribot_notify" {
  filename         = "${path.module}/lambda-functions/contribot_notify/contribot_notify.zip"
  source_code_hash = filebase64sha256("${path.module}/lambda-functions/contribot_notify/contribot_notify.zip")
  function_name    = "func${local.short}ContribotNotify"
  description      = "ContriBot task that notifies moderators about processed lists."
  role             = aws_iam_role.contribot_lambda.arn
  handler          = "handler.handler"
  runtime          = "python3.10"
  timeout          = 60
  memory_size      = 256

  environment {
    variables = local.contribot_lambda_environment
  }

  depends_on = [
    aws_cloudwatch_log_group.contribot_notify,
    aws_iam_role_policy_attachment.contribot_lambda_basic_execution,
  ]

  tags = merge(local.default_tags, {
    Name = "funcContribotNotify"
  })
}

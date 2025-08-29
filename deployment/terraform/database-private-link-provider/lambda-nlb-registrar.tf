# ------------------------------------------------------------------------------
# Lambda Registrar
# ------------------------------------------------------------------------------

locals {
  # Configured to be 3 minutes since it requires a little more than 1 minute to
  # register the NLB targets.
  lambda_nlb_registrar_timeout = 180
}


# Lambda function to register the targets for the NLB after resolution of the
# RDS proxy endpoint

resource "aws_lambda_function" "nlb_targets_registrar" {
  function_name    = "func${local.env_id_short}NlbTargetsRegistrar"
  description      = "Lambda function to register the targets for the NLB after resolution of the RDS proxy endpoint"
  role             = aws_iam_role.lambda_nlb_registrar.arn
  handler          = "register_nlb_targets.handler"
  runtime          = "python3.10"
  filename         = "${path.module}/lambda-nlb-registrar/register_nlb_targets.zip"
  publish          = true
  source_code_hash = filebase64sha256("${path.module}/lambda-nlb-registrar/register_nlb_targets.zip")
  timeout          = local.lambda_nlb_registrar_timeout
  memory_size      = 256

  depends_on = [
    aws_cloudwatch_log_group.nlb_targets_registrar,
  ]

  tags = {
    Name = "functionNlbTargetsRegistrar"
  }
}

# IAM role for the Lambda function

resource "aws_iam_role" "lambda_nlb_registrar" {
  name               = "role${local.env_id_short}NlbTargetsRegistrar"
  assume_role_policy = data.aws_iam_policy_document.lambda_nlb_registrar_assume_role.json

  tags = {
    Name = "roleNlbTargetsRegistrar"
  }
}

data "aws_iam_policy_document" "lambda_nlb_registrar_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_policy" "lambda_nlb_registrar_logging_policy" {
  name   = "policy${local.env_id_short}NlbTargetsRegistrarLogging"
  policy = data.aws_iam_policy_document.lambda_nlb_registrar_logging_policy.json
}

data "aws_iam_policy_document" "lambda_nlb_registrar_logging_policy" {
  statement {
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
    ]
    resources = [
      "arn:aws:logs:*:*:*"
    ]
  }
}

resource "aws_iam_role_policy_attachment" "lambda_nlb_registrar_logging_policy" {
  role       = aws_iam_role.lambda_nlb_registrar.name
  policy_arn = aws_iam_policy.lambda_nlb_registrar_logging_policy.arn
}

resource "aws_iam_policy" "lambda_nlb_registrar_elb_access_policy" {
  name   = "policy${local.env_id_short}NlbTargetsRegistrarElbAccess"
  policy = data.aws_iam_policy_document.lambda_nlb_registrar_elb_access_policy.json
}

data "aws_iam_policy_document" "lambda_nlb_registrar_elb_access_policy" {
  statement {
    sid = "RegisterTargetsSpecificTg"
    actions = [
      "elasticloadbalancing:RegisterTargets",
    ]
    resources = [
      aws_lb_target_group.database_proxy_nlb_tg.arn,
    ]
  }

  statement {
    sid = "DescribeTargetHealthReadOnly"
    actions = [
      "elasticloadbalancing:DescribeTargetHealth",
      "elasticloadbalancing:DescribeTargetGroups",
    ]
    resources = [
      "*",
    ]
  }
}

resource "aws_iam_role_policy_attachment" "lambda_nlb_registrar_elb_access_policy" {
  role       = aws_iam_role.lambda_nlb_registrar.name
  policy_arn = aws_iam_policy.lambda_nlb_registrar_elb_access_policy.arn
}

# Create a CloudWatch log group for the Lambda function

resource "aws_cloudwatch_log_group" "nlb_targets_registrar" {
  name              = "/aws/lambda/func${local.env_id_short}NlbTargetsRegistrar"
  retention_in_days = 14

  tags = {
    Name = "logGroupNlbTargetsRegistrar"
  }
}

# Invoke the Lambda function

data "aws_lambda_invocation" "nlb_targets_registrar" {
  function_name = aws_lambda_function.nlb_targets_registrar.function_name
  input = jsonencode({
    rds_proxy_endpoint   = aws_db_proxy.main_db.endpoint
    nlb_target_group_arn = aws_lb_target_group.database_proxy_nlb_tg.arn
    db_port              = var.db_port
    timeout              = local.lambda_nlb_registrar_timeout
  })

  depends_on = [
    aws_iam_role_policy_attachment.lambda_nlb_registrar_elb_access_policy,
    aws_iam_role_policy_attachment.lambda_nlb_registrar_logging_policy,
  ]
}

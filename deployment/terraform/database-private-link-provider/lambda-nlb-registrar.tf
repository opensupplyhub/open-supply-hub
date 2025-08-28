# ------------------------------------------------------------------------------
# Lambda Registrar
# ------------------------------------------------------------------------------

# Lambda function to register the targets for the NLB after resolution of the
# RDS proxy endpoint

resource "aws_lambda_function" "nlb_targets_registrar" {
  function_name = "func${local.env_id_short}NlbTargetsRegistrar"
  description = "Lambda function to register the targets for the NLB after resolution of the RDS proxy endpoint"
  role = aws_iam_role.lambda_nlb_registrar.arn
  handler = "register_nlb_targets.handler"
  runtime = "python3.10"
  filename = "${path.module}/lambda-nlb-registrar/register_nlb_targets.zip"
  publish = true
  source_code_hash = filebase64sha256("${path.module}/lambda-nlb-registrar/register_nlb_targets.zip")
  timeout = 60

  tags = {
    Name = "functionNlbTargetsRegistrar"
  }
}

# IAM role for the Lambda function

resource "aws_iam_role" "lambda_nlb_registrar" {
  name = "role${local.env_id_short}NlbTargetsRegistrar"
  assume_role_policy = data.aws_iam_policy_document.lambda_nlb_registrar_assume_role.json

  tags = {
    Name = "roleNlbTargetsRegistrar"
  }
}

data "aws_iam_policy_document" "lambda_nlb_registrar_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role_policy" "lambda_nlb_registrar_general_policy" {
  name = "policy${local.env_id_short}NlbTargetsRegistrar"
  role = aws_iam_role.lambda_nlb_registrar.name
  policy = data.aws_iam_policy_document.lambda_nlb_registrar_general_policy.json
}

data "aws_iam_policy_document" "lambda_nlb_registrar_general_policy" {
  statement {
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
    ]
    resources = [aws_cloudwatch_log_group.nlb_targets_registrar.arn]
  }
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
    host = aws_db_proxy.main_db.endpoint
    tg_arn = aws_lb_target_group.database_proxy_nlb_tg.arn
  })
}

output "registrar_result" {
  value = jsondecode(data.aws_lambda_invocation.nlb_targets_registrar.result)
}

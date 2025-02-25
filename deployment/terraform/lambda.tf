#
# Alert Batch failures resources
#
resource "aws_lambda_function" "alert_batch_failures" {
  filename = "${path.module}/lambda-functions/alert_batch_failures/alert_batch_failures.zip"
  # source_code_hash = filebase64sha256(
  #   "${path.module}/lambda-functions/alert_batch_failures/alert_batch_failures.zip",
  # )
  function_name = "func${local.short}AlertBatchFailures"
  description   = "Function to alert on AWS Batch Job Failures."
  role          = aws_iam_role.alert_batch_failures.arn
  handler       = "alert_batch_failures.handler"
  runtime       = "python3.8"
  timeout       = 10
  memory_size   = 128

  environment {
    variables = {
      ENVIRONMENT                      = var.environment
      ROLLBAR_SERVER_SIDE_ACCESS_TOKEN = var.rollbar_server_side_access_token
    }
  }

  tags = {
    Project     = var.project
    Environment = var.environment
  }
}

resource "aws_cloudwatch_event_rule" "alert_batch_failures" {
  name        = "rule${local.short}AlertBatchFailures"
  description = "Rule to send alerts when batch jobs fail."

  event_pattern = <<PATTERN
{
  "source": ["aws.batch"],
  "detail-type": ["Batch Job State Change"],
  "detail": {
    "status": ["FAILED"],
    "jobQueue": [
      "${aws_batch_job_queue.default.arn}"
    ]
  }
}
PATTERN

}

resource "aws_cloudwatch_event_target" "alert_batch_failures" {
  rule      = aws_cloudwatch_event_rule.alert_batch_failures.name
  target_id = "target${local.short}AlertBatchFailures"
  arn       = aws_lambda_function.alert_batch_failures.arn
}

resource "aws_lambda_permission" "alert_batch_failures" {
  statement_id  = "perm${local.short}AlertBatchFailures"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.alert_batch_failures.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.alert_batch_failures.arn
}

#
# Alert Step Functions failures resources
#
resource "aws_lambda_function" "alert_sfn_failures" {
  filename = "${path.module}/lambda-functions/alert_sfn_failures/alert_sfn_failures.zip"
  # source_code_hash = filebase64sha256(
  #   "${path.module}/lambda-functions/alert_sfn_failures/alert_sfn_failures.zip",
  # )
  function_name = "func${local.short}AlertStepFunctionsFailures"
  description   = "Function to alert on AWS Step Functions Failures."
  role          = aws_iam_role.alert_sfn_failures.arn
  handler       = "alert_sfn_failures.handler"
  runtime       = "python3.8"
  timeout       = 10
  memory_size   = 128

  environment {
    variables = {
      ENVIRONMENT                      = var.environment
      ROLLBAR_SERVER_SIDE_ACCESS_TOKEN = var.rollbar_server_side_access_token
    }
  }

  tags = {
    Project     = var.project
    Environment = var.environment
  }
}


#
# Redirect to S3 origin
#

data "aws_iam_policy_document" "lambda_edge_redirect_to_s3_origin_assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com", "edgelambda.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

data "aws_iam_policy_document" "lambda_edge_redirect_to_s3_origin_exec_role_policy" {
  statement {
    sid = "1"
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources = [
      "arn:aws:logs:*:*:*"
    ]
  }
}

resource "aws_iam_role" "lambda_edge_redirect_to_s3_origin" {
  name               = "role${local.short}RedirectToS3origin"
  assume_role_policy = data.aws_iam_policy_document.lambda_edge_redirect_to_s3_origin_assume_role.json
}

resource "aws_iam_role_policy" "lambda_edge_redirect_to_s3_origin_exec_role" {
  role   = aws_iam_role.lambda_edge_redirect_to_s3_origin.id
  policy = data.aws_iam_policy_document.lambda_edge_redirect_to_s3_origin_exec_role_policy.json
}

# data "archive_file" "lambda_edge_redirect_to_s3_origin" {
#   type        = "zip"
#   source_file = "lambda-functions/redirect_to_s3_origin/index.mjs"
#   output_path = "/tmp/redirect_to_s3_origin_${timestamp()}.zip"
# }

# data "archive_file" "lambda_edge_redirect_to_s3_origin" {
#   type        = "zip"
#   output_path = "/tmp/redirect_to_s3_origin.zip"
#   source {
#     content  = <<EOF
# 'use strict';
#
# export const handler = async (event) => {
#     const request = event.Records[0].cf.request;
#     if (request.uri === '/') {
#         request.uri = '/index.html';
#     }
#     return request;
# }
# EOF
#     filename = "index.mjs"
#   }
# }

resource "aws_lambda_function" "redirect_to_s3_origin" {
  filename         = "lambda-functions/redirect_to_s3_origin/redirect_to_s3_origin.zip"
  function_name    = "func${local.short}RedirectToS3origin"
  role             = aws_iam_role.lambda_edge_redirect_to_s3_origin.arn
  handler          = "index.handler"
  publish          = true
  runtime          = "nodejs18.x"
  provider         = aws.certificates

  depends_on = [
    aws_iam_role.lambda_edge_redirect_to_s3_origin,
    aws_cloudwatch_log_group.redirect_to_s3_origin,
  ]
}

resource "aws_cloudwatch_log_group" "redirect_to_s3_origin" {
  name              = "/aws/lambda/func${local.short}RedirectToS3origin"
  retention_in_days = 14
}

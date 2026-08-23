#
# Route 53 public hosted zone query logging
#
# Satisfies the Vanta SOC 2 test "Route53 query logging enabled (AWS)", which
# requires every public hosted zone to log DNS queries to a CloudWatch Logs log
# group.
#
# Two constraints shape this file:
#
#   1. AWS requires both the log group and the CloudWatch Logs resource policy
#      that lets Route 53 write into it to live in us-east-1, regardless of the
#      region the rest of the stack runs in (eu-west-1). Hence the dedicated
#      aws.us_east_1 provider. The aws_route53_query_log resource itself talks
#      to the global Route 53 endpoint and uses the default provider.
#      https://docs.aws.amazon.com/Route53/latest/APIReference/API_CreateQueryLoggingConfig.html
#
#   2. Several environments share one public hosted zone inside a single AWS
#      account (see the DMARC comment in dns.tf), and a zone can hold only one
#      query logging configuration. Each zone must therefore be owned by exactly
#      one environment, or two Terraform states will fight over it.
#
# Ownership is declared in deployment/environments/terraform-<env>.tfvars rather
# than hardcoded here, so moving a zone between environments is a one-line
# change in the file that already describes that environment:
#
#   route53_query_logging_enabled  opts an environment in for the zone it points
#                                  at via r53_public_hosted_zone.
#   route53_query_log_extra_zones  covers zones that are not any environment's
#                                  r53_public_hosted_zone.
#
# Current owners:
#
#   opensupplyhub.org          -> Production   (Rba points at it, opts out)
#   openapparel.org            -> Production   (via route53_query_log_extra_zones)
#   staging.opensupplyhub.org  -> Staging
#   os-hub.net                 -> Development  (Test and Preprod point at it, opt out)
#
# os-hub.net sits with Development rather than Test because Development is
# deployed automatically on every push to main and is not offered by the
# Destroy Environment workflow, so its query logging configuration is not torn
# down and recreated the way Preprod's would be.
#
# Private hosted zones (osh.internal) are out of scope: Route 53 query logging
# supports public zones only.
#

locals {
  # True for any environment that creates at least one query logging
  # configuration, and therefore needs the resource policy.
  route53_query_logging_owner = (
    var.route53_query_logging_enabled ||
    length(var.route53_query_log_extra_zones) > 0
  )
}

# One resource policy per Terraform state, scoped to every /aws/route53/* log
# group in the account. Naming it per environment keeps each state self
# contained, so an environment can enable query logging without waiting on
# another environment's apply. CloudWatch Logs allows up to 10 resource policies
# per region per account, which leaves ample headroom.
data "aws_iam_policy_document" "route53_query_logging" {
  statement {
    sid    = "Route53QueryLogsDelivery"
    effect = "Allow"

    actions = [
      "logs:CreateLogStream",
      "logs:PutLogEvents",
    ]

    principals {
      type        = "Service"
      identifiers = ["route53.amazonaws.com"]
    }

    resources = [
      "arn:aws:logs:us-east-1:${data.aws_caller_identity.current.account_id}:log-group:/aws/route53/*",
    ]

    # Guards against the confused deputy problem: only our own account's hosted
    # zones may write into these log groups.
    condition {
      test     = "StringEquals"
      variable = "aws:SourceAccount"
      values   = [data.aws_caller_identity.current.account_id]
    }
  }
}

resource "aws_cloudwatch_log_resource_policy" "route53_query_logging" {
  provider = aws.us_east_1

  count = local.route53_query_logging_owner ? 1 : 0

  policy_name     = "${lower(replace(var.project, " ", ""))}-${lower(var.environment)}-route53-query-logging"
  policy_document = data.aws_iam_policy_document.route53_query_logging.json
}

#
# The public hosted zone this environment points at.
#
resource "aws_cloudwatch_log_group" "route53_query_log_public" {
  provider = aws.us_east_1

  count = var.route53_query_logging_enabled ? 1 : 0

  name              = "/aws/route53/${var.r53_public_hosted_zone}"
  retention_in_days = var.route53_query_log_retention_days

  tags = {
    Name        = "/aws/route53/${var.r53_public_hosted_zone}"
    Project     = var.project
    Environment = var.environment
  }
}

resource "aws_route53_query_log" "public" {
  count = var.route53_query_logging_enabled ? 1 : 0

  zone_id                  = data.aws_route53_zone.external.zone_id
  cloudwatch_log_group_arn = aws_cloudwatch_log_group.route53_query_log_public[0].arn

  # Route 53 rejects the configuration if the resource policy is not already in
  # place. Terraform cannot infer this dependency, so declare it explicitly.
  depends_on = [aws_cloudwatch_log_resource_policy.route53_query_logging]
}

#
# Zones this environment owns that it does not otherwise reference - today only
# openapparel.org, the legacy domain still served out of the Production account.
#
data "aws_route53_zone" "route53_query_log_extra" {
  for_each = toset(var.route53_query_log_extra_zones)

  name         = each.value
  private_zone = false
}

resource "aws_cloudwatch_log_group" "route53_query_log_extra" {
  provider = aws.us_east_1

  for_each = toset(var.route53_query_log_extra_zones)

  name              = "/aws/route53/${each.value}"
  retention_in_days = var.route53_query_log_retention_days

  tags = {
    Name        = "/aws/route53/${each.value}"
    Project     = var.project
    Environment = var.environment
  }
}

resource "aws_route53_query_log" "extra" {
  for_each = toset(var.route53_query_log_extra_zones)

  zone_id                  = data.aws_route53_zone.route53_query_log_extra[each.value].zone_id
  cloudwatch_log_group_arn = aws_cloudwatch_log_group.route53_query_log_extra[each.value].arn

  depends_on = [aws_cloudwatch_log_resource_policy.route53_query_logging]
}

resource "random_id" "database_anonymizer" {
  byte_length = 4
}

data "aws_caller_identity" "current" {}

data "aws_iam_policy_document" "kms" {

  statement {
    sid = "Enable IAM User Permissions"
    actions = [
      "kms:*",
    ]
    principals {
      identifiers = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"]
      type        = "AWS"
    }
    resources = ["*"]
  }

  statement {
    sid = "Allow access for Key Administrators"
    actions = [
      "kms:Create*",
      "kms:Describe*",
      "kms:Enable*",
      "kms:List*",
      "kms:Put*",
      "kms:Update*",
      "kms:Revoke*",
      "kms:Disable*",
      "kms:Get*",
      "kms:Delete*",
      "kms:TagResource",
      "kms:UntagResource",
      "kms:ScheduleKeyDeletion",
      "kms:CancelKeyDeletion"
    ]
    principals {
      identifiers = concat(var.kms_key_admin_users, [
        module.database_anonymizer_task_definition.aws_iam_role_ecs_task_execution_role_arn
      ])
      type = "AWS"
    }
    resources = ["*"]
  }

  statement {
    sid = "Allow use of the key"
    actions = [
      "kms:Encrypt",
      "kms:Decrypt",
      "kms:ReEncrypt*",
      "kms:GenerateDataKey*",
      "kms:DescribeKey"
    ]
    principals {
      identifiers = concat(var.kms_key_admin_users, [
        "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root",
        module.database_anonymizer_task_definition.aws_iam_role_ecs_task_execution_role_arn,
        "arn:aws:iam::${var.destination_aws_account}:root"
      ])
      type = "AWS"
    }
    resources = ["*"]
  }
  statement {
    sid = "Allow attachment of persistent resources"
    actions = [
      "kms:RevokeGrant",
      "kms:ListGrants",
      "kms:CreateGrant"
    ]
    principals {
      identifiers = concat(var.kms_key_admin_users, [
        "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root",
        module.database_anonymizer_task_definition.aws_iam_role_ecs_task_execution_role_arn,
        "arn:aws:iam::${var.destination_aws_account}:root"
      ])
      type = "AWS"
    }
    resources = ["*"]
    condition {
      test     = "Bool"
      values   = ["true"]
      variable = "kms:GrantIsForAWSResource"
    }
  }

}

module "rds-kms" {
  source = "git::https://github.com/cloudposse/terraform-aws-kms-key//?ref=0.12.2"

  name                    = local.kms_key_name
  description             = "Cross account kms key for RDS snapshot"
  deletion_window_in_days = 10
  enable_key_rotation     = false
  multi_region            = false
  alias                   = "alias/${local.kms_key_name}"
  policy                  = data.aws_iam_policy_document.kms.json
}

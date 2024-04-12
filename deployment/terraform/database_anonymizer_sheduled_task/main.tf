locals {
  database_anonymizer_image = "${module.ecr_repository_database_anonymizer.repository_url}:${var.database_anonymizer_image_tag}"
}

resource "aws_cloudwatch_log_group" "database_anonymizer" {
  name              = "log${local.short}DatabaseAnonymizer"
  retention_in_days = 30
}

data "aws_iam_policy_document" "database_anonymizer_worker" {
  statement {
    actions = [
      "rds:*",
    ]
    resources = ["*"]
  }

  statement {
    actions = [
      "ssm:DescribeParameters"
    ]
    resources = ["*"]
  }

  statement {
    actions = [
      "ssm:GetParameters"
    ]
    resources = [
      aws_ssm_parameter.database_password.arn
    ]
  }
}

module "database_anonymizer_cluster" {
  source = "github.com/cn-terraform/terraform-aws-ecs-cluster?ref=1.0.11"
  name   = join("-", [local.short, "DatabaseAnonymizer"])
}

resource "aws_ssm_parameter" "database_password" {
  name        = "/database/${var.rds_database_identifier}/password"
  description = "The database ${var.rds_database_identifier} password"
  type        = "String"
  value       = var.rds_database_password
}

module "database_anonymizer_task_definition" {
  source          = "github.com/cn-terraform/terraform-aws-ecs-fargate-task-definition?ref=1.0.36"
  name_prefix     = "database-anonymizer"
  container_image = local.database_anonymizer_image
  container_name  = "database-anonymizer"

  ecs_task_execution_role_custom_policies = [
    data.aws_iam_policy_document.database_anonymizer_worker.json
  ]

  environment = [
    {
      name : "SOURCE_DATABASE_IDENTIFIER"
      value : var.rds_database_identifier
    },
    {
      name : "SOURCE_DATABASE_USER"
      value : var.rds_database_username
    },
    {
      name : "SOURCE_DATABASE_NAME"
      value : var.rds_database_name
    },
    {
      name : "DESTINATION_AWS_ACCOUNT"
      value : var.destination_aws_account
    },
    {
      name : "ANONYMIZER_DATABASE_IDENTIFIER"
      value : var.anonymizer_db_identifier
    },
    {
      name : "ANONYMIZER_DATABASE_INSTANCE_TYPE"
      value : var.rds_instance_type
    },
    {
      name : "DATABASE_SUBNET_GROUP_NAME"
      value : var.database_subnet_group_name
    },
    {
      name : "DATABASE_SECURITY_GROUP_IDS"
      value : var.database_security_group_ids
    },
    {
      name : "KMS_KEY"
      value : module.rds-kms.key_id
    },
    {
      name : "AWS_REGION"
      value : var.aws_region
    }
  ]

  secrets = [
    {
       valueFrom: aws_ssm_parameter.database_password.arn
       name: "SOURCE_DATABASE_PASSWORD"
    },
  ]

  log_configuration = {
    logDriver : "awslogs",
    options : {
      "awslogs-group" : aws_cloudwatch_log_group.database_anonymizer.name,
      "awslogs-region" : var.aws_region,
      "awslogs-stream-prefix" : "database-anonymizer"
    }
  }
}

module "database_anonymizer_task" {
  source                                      = "github.com/cn-terraform/terraform-aws-ecs-fargate-scheduled-task?ref=1.0.25"
  name_prefix                                 = "anonymize_database-task"
  event_rule_name                             = "anonymize_database-rule"
  event_rule_schedule_expression              = var.schedule_expression
  ecs_cluster_arn                             = module.database_anonymizer_cluster.aws_ecs_cluster_cluster_arn
  event_target_ecs_target_subnets             = var.subnet_ids
  event_target_ecs_target_security_groups     = var.security_group_ids
  event_target_ecs_target_task_definition_arn = module.database_anonymizer_task_definition.aws_ecs_task_definition_td_arn
  ecs_execution_task_role_arn                 = module.database_anonymizer_task_definition.aws_iam_role_ecs_task_execution_role_arn
  ecs_task_role_arn                           = module.database_anonymizer_task_definition.aws_iam_role_ecs_task_execution_role_arn
}

module "ecr_repository_database_anonymizer" {
  source = "github.com/azavea/terraform-aws-ecr-repository?ref=1.0.0"

  repository_name         = "${lower(replace(var.project, " ", ""))}-database-anonymizer-${lower(var.environment)}"
  attach_lifecycle_policy = true
}

resource "aws_cloudwatch_log_group" "this" {
  name              = "log${local.short}AnonymizedDatabaseDump"
  retention_in_days = 30
}

data "aws_iam_policy_document" "this" {
  statement {
    actions = [
      "rds:*",
    ]
    resources = ["*"]
  }

  statement {
    actions = [
      "kms:*",
    ]
    resources = ["*"]
  }

  statement {
    actions = [
      "s3:*",
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

module "anonymized_database_dump_cluster" {
  source = "github.com/cn-terraform/terraform-aws-ecs-cluster?ref=1.0.11"
  name   = join("-", [local.short, "AnonymizedDatabaseDump"])
}

resource "aws_ssm_parameter" "database_password" {
  name        = "/database/${var.anonymized_database_identifier}/password"
  description = "The database ${var.anonymized_database_identifier} password"
  type        = "String"
  value       = var.anonymized_database_password
}

module "anonymized_database_dump_task_definition" {
  source          = "github.com/cn-terraform/terraform-aws-ecs-fargate-task-definition?ref=1.0.36"
  name_prefix     = "anonymized-database-dump"
  container_image = local.anonymized_database_dump_image
  container_name  = "anonymized-database-dump"

  ecs_task_execution_role_custom_policies = [
    data.aws_iam_policy_document.this.json
  ]

  environment = [
    {
      name : "DATABASE_USERNAME"
      value : var.anonymized_database_username
    },
    {
      name : "DATABASE_NAME"
      value : var.anonymized_database_name
    },
    {
      name : "TEMPORARY_INSTANCE_CLASS"
      value : var.anonymized_database_instance_type
    },
    {
      name : "SUBNET_GROUP_ID"
      value : var.anonymized_database_subnet_group_name
    },
    {
      name : "DB_INSTANCE_IDENTIFIER"
      value : var.anonymized_database_identifier
    },
    {
      name : "KMS_KEY_ID"
      value : var.anonymized_database_kms_key_id
    }
  ]

  secrets = [
    {
       valueFrom: aws_ssm_parameter.database_password.arn
       name: "DATABASE_PASSWORD"
    },
  ]

  log_configuration = {
    logDriver : "awslogs",
    options : {
      "awslogs-group" : aws_cloudwatch_log_group.this.name,
      "awslogs-region" : var.aws_region,
      "awslogs-stream-prefix" : "anonymized-database-dump"
    }
  }
}

module "database_anonymizer_task" {
  source                                      = "github.com/cn-terraform/terraform-aws-ecs-fargate-scheduled-task?ref=1.0.25"
  name_prefix                                 = "anonymized-database-dump-task"
  event_rule_name                             = "anonymized-database-dump-rule"
  event_rule_schedule_expression              = var.anonymized_database_schedule_expression
  ecs_cluster_arn                             = module.anonymized_database_dump_cluster.aws_ecs_cluster_cluster_arn
  event_target_ecs_target_subnets             = var.anonymized_database_subnet_ids
  event_target_ecs_target_security_groups     = var.anonymized_database_security_group_ids
  event_target_ecs_target_task_definition_arn = module.anonymized_database_dump_task_definition.aws_ecs_task_definition_td_arn
  ecs_execution_task_role_arn                 = module.anonymized_database_dump_task_definition.aws_iam_role_ecs_task_execution_role_arn
  ecs_task_role_arn                           = module.anonymized_database_dump_task_definition.aws_iam_role_ecs_task_execution_role_arn
}

module "ecr_repository_database_anonymizer" {
  source = "github.com/azavea/terraform-aws-ecr-repository?ref=1.0.0"

  repository_name         = "${lower(replace(var.project, " ", ""))}-anonymized-database-dump-${lower(var.environment)}"
  attach_lifecycle_policy = true
}

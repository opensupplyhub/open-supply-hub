locals {
 database_anonymizer_image = "${module.ecr_repository_database_anonymizer.repository_url}:${var.database_anonymizer_image_tag}"
}

resource "aws_cloudwatch_log_group" "database_anonymizer" {
  name              = "log${local.short}DatabaseAnonymizer"
  retention_in_days = 30
}

data "aws_iam_policy_document" "database_anonymizer_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }

}

data "aws_iam_policy_document" "database_anonymizer_worker" {
  statement {
    actions = [
      "rds:*",
      "ecr:GetAuthorizationToken",
      "ecr:BatchCheckLayerAvailability",
      "ecr:GetDownloadUrlForLayer",
      "ecr:BatchGetImage",
      "logs:CreateLogStream",
      "logs:DescribeLogGroups",
      "logs:DescribeLogStreams",
      "logs:PutLogEvents"
    ]
    resources = ["*"]
  }
}

resource "aws_iam_role" "database_anonymizer" {
  name       = join("-", [local.short, "DatabaseAnonymizer"])
  assume_role_policy = data.aws_iam_policy_document.database_anonymizer_assume_role.json
}

resource "aws_iam_policy" "database_anonymizer" {
  name = join("-", [local.short, "DatabaseAnonymizer"])
  path        = "/"
  policy      = data.aws_iam_policy_document.database_anonymizer_worker.json
}

resource "aws_iam_role_policy_attachment" "database_anonymizer" {
  role       = aws_iam_role.database_anonymizer.name
  policy_arn = aws_iam_policy.database_anonymizer.arn
}

# AWS ECS Cluster Terraform Module
# https://registry.terraform.io/modules/cn-terraform/ecs-cluster/aws/latest
module "database_anonymizer_cluster" {
  source  = "git::git@github.com:cn-terraform/terraform-aws-ecs-cluster.git?ref=1.0.11"
  name    = join("-", [local.short, "DatabaseAnonymizer"])
}

# AWS ECS Fargate Task Definition Terraform Module
# https://registry.terraform.io/modules/cn-terraform/ecs-fargate-task-definition/aws/latest
module "database_anonymizer_task_definition" {
  source                 = "git@github.com:cn-terraform/terraform-aws-ecs-fargate-task-definition.git?ref=1.0.36"
  name_prefix            = "database-anonymizer"
  container_image        = local.database_anonymizer_image
  container_name         = "database-anonymizer"
  execution_role_arn     = aws_iam_role.database_anonymizer.arn
  task_role_arn          = aws_iam_role.database_anonymizer.arn

  environment = [
      {
          name: "SOURCE_DATABASE_IDENTIFIER"
          value: var.rds_database_identifier
      },
      {
          name: "SOURCE_DATABASE_PASSWORD"
          value: var.rds_database_password
      },
      {
          name: "SOURCE_DATABASE_USER"
          value: var.rds_database_username
      },
      {
          name: "SOURCE_DATABASE_NAME"
          value: var.rds_database_name
      },
      {
          name: "DESTINATION_AWS_ACCOUNT"
          value: var.destination_aws_account
      },
      {
          name: "ANONYMIZER_DATABASE_IDENTIFIER"
          value: var.anonymizer_db_identifier
      }
  ]

#  secrets = [
#    {
#       valueFrom: "arn:aws:ssm:eu-west-1:343975343274:parameter/test",
#       name: "TEST"
#    },
#  ]

  log_configuration = {
    logDriver: "awslogs",
    options: {
      "awslogs-group": aws_cloudwatch_log_group.database_anonymizer.name,
      "awslogs-region": var.aws_region,
      "awslogs-stream-prefix": "database-anonymizer"
    }
  }

  depends_on = [
    aws_iam_role.database_anonymizer
  ]
}

# AWS ECS Fargate Schedule Task Terraform Module
# https://registry.terraform.io/modules/cn-terraform/ecs-fargate-scheduled-task/aws/latest
module "database_anonymizer_task" {
  source                                      = "git::git@github.com:cn-terraform/terraform-aws-ecs-fargate-scheduled-task.git?ref=1.0.25"
  name_prefix                                 = "anonymize_database-task"
  event_rule_name                             = "anonymize_database-rule"
  event_rule_schedule_expression              = var.schedule_expression
  ecs_cluster_arn                             = module.database_anonymizer_cluster.aws_ecs_cluster_cluster_arn
  event_target_ecs_target_subnets             = var.subnet_ids
  event_target_ecs_target_security_groups     = var.security_group_ids
  event_target_ecs_target_task_definition_arn = module.database_anonymizer_task_definition.aws_ecs_task_definition_td_arn
  ecs_execution_task_role_arn                 = aws_iam_role.database_anonymizer.arn
  ecs_task_role_arn                           = aws_iam_role.database_anonymizer.arn
}

module "ecr_repository_database_anonymizer" {
  source = "github.com/azavea/terraform-aws-ecr-repository?ref=1.0.0"

  repository_name =  "${lower(replace(var.project, " ", ""))}-database-anonymizer-${lower(var.environment)}"
  attach_lifecycle_policy = true
}

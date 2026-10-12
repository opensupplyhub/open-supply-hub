#
# Database restore task (OSDEV-3588)
#
# One-off Fargate task that restores the anonymized production dump
# (s3://<bucket>/<key>, produced weekly by anonymized_database_dump) into
# this environment's database. It runs inside the VPC and talks to RDS
# directly, instead of pushing the dump through the bastion with an SSM port
# forward, which is too slow for a multi-GB restore.
#
# Started by the workflows with deployment/run_restore_task; the image is
# src/anon-tools/Dockerfile.restore (docker-bake.hcl target
# "database-restore").
#

module "ecr_repository_database_restore" {
  count  = var.database_restore_enabled ? 1 : 0
  source = "./modules/ecr-repository"

  repository_name         = "${lower(replace(var.project, " ", ""))}-database-restore-${lower(var.environment)}"
  image_tag_mutability    = "IMMUTABLE"
  attach_lifecycle_policy = true
}

resource "aws_cloudwatch_log_group" "database_restore" {
  count = var.database_restore_enabled ? 1 : 0

  name              = "log${local.short}DatabaseRestore"
  retention_in_days = 365
}

resource "aws_security_group" "database_restore" {
  count = var.database_restore_enabled ? 1 : 0

  vpc_id = module.vpc.id

  tags = {
    Name        = "sgDatabaseRestore"
    Project     = var.project
    Environment = var.environment
  }
}

resource "aws_security_group_rule" "database_restore_rds_enc_egress" {
  count = var.database_restore_enabled ? 1 : 0

  type      = "egress"
  from_port = module.database_enc.port
  to_port   = module.database_enc.port
  protocol  = "tcp"

  security_group_id        = aws_security_group.database_restore[0].id
  source_security_group_id = module.database_enc.database_security_group_id
}

# S3 (the dump), ECR (the image) and CloudWatch Logs, through the NAT gateway.
resource "aws_security_group_rule" "database_restore_https_egress" {
  count = var.database_restore_enabled ? 1 : 0

  type             = "egress"
  from_port        = 443
  to_port          = 443
  protocol         = "tcp"
  cidr_blocks      = ["0.0.0.0/0"]
  ipv6_cidr_blocks = ["::/0"]

  security_group_id = aws_security_group.database_restore[0].id
}

resource "aws_security_group_rule" "rds_enc_database_restore_ingress" {
  count = var.database_restore_enabled ? 1 : 0

  type      = "ingress"
  from_port = module.database_enc.port
  to_port   = module.database_enc.port
  protocol  = "tcp"

  security_group_id        = module.database_enc.database_security_group_id
  source_security_group_id = aws_security_group.database_restore[0].id
}

# Task role: read the dump. The execution role is the shared
# ecs_task_execution_role, which already pulls from ECR, writes logs and
# reads the RDS master secret injected below.
resource "aws_iam_role" "database_restore_task" {
  count = var.database_restore_enabled ? 1 : 0

  name               = "ecs${local.short}DatabaseRestoreTaskRole"
  assume_role_policy = data.aws_iam_policy_document.ecs_assume_role.json
}

data "aws_iam_policy_document" "database_restore_task" {
  statement {
    effect    = "Allow"
    actions   = ["s3:GetObject"]
    resources = ["arn:aws:s3:::${var.database_restore_dump_s3_bucket}/${var.database_restore_dump_s3_key}"]
  }
}

resource "aws_iam_role_policy" "database_restore_task" {
  count = var.database_restore_enabled ? 1 : 0

  name   = "DatabaseRestoreReadDump"
  role   = aws_iam_role.database_restore_task[0].name
  policy = data.aws_iam_policy_document.database_restore_task.json
}

resource "aws_ecs_task_definition" "database_restore" {
  count = var.database_restore_enabled ? 1 : 0

  family                   = "${local.short}DatabaseRestore"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.database_restore_fargate_cpu
  memory                   = var.database_restore_fargate_memory

  ephemeral_storage {
    size_in_gib = var.database_restore_ephemeral_storage_gib
  }

  task_role_arn      = aws_iam_role.database_restore_task[0].arn
  execution_role_arn = aws_iam_role.ecs_task_execution_role.arn

  container_definitions = jsonencode([
    {
      name      = "database-restore"
      image     = "${module.ecr_repository_database_restore[0].repository_url}:${var.image_tag}"
      essential = true

      environment = [
        { name = "DATABASE_HOST", value = aws_route53_record.database.name },
        { name = "DATABASE_PORT", value = tostring(module.database_enc.port) },
        { name = "DATABASE_NAME", value = var.rds_database_name },
        { name = "DUMP_S3_URI", value = "s3://${var.database_restore_dump_s3_bucket}/${var.database_restore_dump_s3_key}" },
        { name = "RESTORE_JOBS", value = tostring(var.database_restore_jobs) },
        { name = "AWS_DEFAULT_REGION", value = var.aws_region },
      ]

      secrets = [
        { name = "DATABASE_USERNAME", valueFrom = "${local.rds_master_secret_arn}:username::" },
        { name = "DATABASE_PASSWORD", valueFrom = "${local.rds_master_secret_arn}:password::" },
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.database_restore[0].name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "restore"
        }
      }
    }
  ])
}

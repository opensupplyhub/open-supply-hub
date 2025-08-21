#------------------------------------------------------------------------------
# RDS Proxy Module
#------------------------------------------------------------------------------

# Create a name for the database proxy
locals {
  env_id_short = "${replace(var.project_identifier, " ", "")}${var.env_identifier}"
  proxy_name = lower("database-${var.project_identifier}-${var.env_identifier}-proxy")
}


# Proxy for the database
resource "aws_db_proxy" "main_db" {
  name                   = local.proxy_name
  debug_logging          = var.debug_logging
  engine_family          = "POSTGRESQL"
  idle_client_timeout    = var.idle_client_timeout
  require_tls            = true
  role_arn               = aws_iam_role.proxy_role.arn
  vpc_security_group_ids = [aws_security_group.proxy.id]
  vpc_subnet_ids         = var.subnet_ids

  auth {
    auth_scheme = "SECRETS"
    iam_auth    = "DISABLED"
    secret_arn  = aws_secretsmanager_secret.proxy_secret.arn
  }

  tags = {
    Name = "databaseProxy"
  }
}

# RDS Proxy Default Target Group
resource "aws_db_proxy_default_target_group" "default" {
  db_proxy_name = aws_db_proxy.main_db.name

  connection_pool_config {
    connection_borrow_timeout    = var.connection_borrow_timeout
    max_connections_percent      = var.max_connections_percent
    max_idle_connections_percent = var.max_idle_connections_percent
  }
}

# RDS Proxy Target Group Association
resource "aws_db_proxy_target" "main" {
  db_instance_identifier = var.db_instance_identifier
  db_proxy_name          = aws_db_proxy.main_db.name
  target_group_name      = aws_db_proxy_default_target_group.default.name
}

# Security Group for RDS Proxy
resource "aws_security_group" "proxy" {
  name = "sg${local.env_id_short}DatabaseProxy"
  description = "Security group for RDS proxy"
  vpc_id      = var.vpc_id

  tags = {
    Name = "sgDatabaseProxy"
  }
}

# Security group rules for RDS proxy
resource "aws_security_group_rule" "proxy_ingress" {
  type                     = "ingress"
  from_port                = 5432
  to_port                  = 5432
  protocol                 = "tcp"

  source_security_group_id = var.allowed_security_group_id
  security_group_id        = aws_security_group.proxy.id
  description              = "Allow PostgreSQL access from specified security groups"
}

resource "aws_security_group_rule" "proxy_egress" {
  type                     = "egress"
  from_port                = 0
  to_port                  = 0
  protocol                 = "-1"
  cidr_blocks              = ["0.0.0.0/0"]

  security_group_id        = aws_security_group.proxy.id
  description              = "Allow all outbound traffic"
}

# Secret for RDS proxy
resource "aws_secretsmanager_secret" "proxy_secret" {
  name = "database${local.env_id_short}ProxySecret"
  recovery_window_in_days = 0

  tags = {
    Name = "databaseProxySecret"
  }
}

# Secret version for RDS proxy
resource "aws_secretsmanager_secret_version" "proxy_secret_version" {
  secret_id = aws_secretsmanager_secret.proxy_secret.id
  secret_string = jsonencode({
    username = var.db_username
    password = var.db_password
  })
}

# IAM role for RDS proxy
resource "aws_iam_role" "proxy_role" {
  name = "database${local.env_id_short}ProxyRole"

  assume_role_policy = data.aws_iam_policy_document.proxy_assume_role_policy.json

  tags = {
    Name = "databaseProxyRole"
  }
}

data "aws_iam_policy_document" "proxy_assume_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["rds.amazonaws.com"]
    }
  }
}

# IAM policy for RDS proxy
resource "aws_iam_role_policy" "proxy_policy" {
  name = "database${local.env_id_short}ProxyPolicy"
  role = aws_iam_role.proxy_role.id

  policy = data.aws_iam_policy_document.proxy_policy.json
}

data "aws_iam_policy_document" "proxy_policy" {
  statement {
    effect = "Allow"
    actions = ["secretsmanager:GetSecretValue"]
    resources = [aws_secretsmanager_secret.proxy_secret.arn]
  }
}

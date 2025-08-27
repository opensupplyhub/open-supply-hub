#------------------------------------------------------------------------------
# RDS Proxy
#------------------------------------------------------------------------------

# RDS proxy for the database

resource "aws_db_proxy" "main_db" {
  name                   = lower("database-${var.project_identifier}-${var.env_identifier}-proxy")
  debug_logging          = var.db_proxy_debug_logging
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

# RDS proxy default target group

resource "aws_db_proxy_default_target_group" "default" {
  db_proxy_name = aws_db_proxy.main_db.name

  connection_pool_config {
    connection_borrow_timeout    = var.connection_borrow_timeout
    max_connections_percent      = var.max_connections_percent
    max_idle_connections_percent = var.max_idle_connections_percent
  }
}

# RDS proxy target group association

resource "aws_db_proxy_target" "main" {
  db_instance_identifier = var.db_instance_identifier
  db_proxy_name          = aws_db_proxy.main_db.name
  target_group_name      = aws_db_proxy_default_target_group.default.name
}

# Security group for RDS proxy

resource "aws_security_group" "proxy" {
  name = "sg${local.env_id_short}DatabaseProxy"
  description = "Security group for RDS proxy"
  vpc_id      = var.vpc_id

  tags = {
    Name = "sgDatabaseProxy"
  }
}

# Security group rules for RDS proxy

resource "aws_security_group_rule" "proxy_database_egress" {
  type                     = "egress"
  from_port                = var.db_port
  to_port                  = var.db_port
  protocol                 = "tcp"
  
  security_group_id        = aws_security_group.proxy.id
  source_security_group_id = var.database_security_group_id
  description              = "Allow outgoing traffic from RDS proxy to the database"
}

resource "aws_security_group_rule" "nlb_proxy_ingress" {
  type                     = "ingress"
  from_port                = var.db_port
  to_port                  = var.db_port
  protocol                 = "tcp"

  security_group_id        = aws_security_group.proxy.id
  source_security_group_id = aws_security_group.database_proxy_nlb_sg.id
  description              = "Allow incoming traffic from NLB to the database proxy"
}

# Security group rules for RDS instance

resource "aws_security_group_rule" "proxy_db_ingress" {
  type                     = "ingress"
  from_port                = var.db_port
  to_port                  = var.db_port
  protocol                 = "tcp"

  security_group_id        = var.database_security_group_id
  source_security_group_id = aws_security_group.proxy.id
  description              = "Allow incoming traffic from RDS proxy to the database"
}

# Secret for RDS proxy

resource "aws_secretsmanager_secret" "proxy_secret" {
  name = "db${local.env_id_short}ProxySecret"
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

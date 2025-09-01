# ------------------------------------------------------------------------------
# VPC Endpoint
# ------------------------------------------------------------------------------

locals {
  env_id_short = "${replace(var.project_identifier, " ", "")}${var.env_identifier}"
}

# VPC endpoint to connect to the source database for the synchronization job

resource "aws_vpc_endpoint" "database_vpc_endpoint" {
  vpc_id             = var.vpc_id
  subnet_ids         = var.subnet_ids
  service_name       = var.vpc_endpoint_service_name
  vpc_endpoint_type  = "Interface"
  security_group_ids = [aws_security_group.database_vpc_endpoint_sg.id]

  tags = {
    Name = "databaseVpcEndpoint"
  }
}

# Security group for the VPC endpoint

resource "aws_security_group" "database_vpc_endpoint_sg" {
  name   = "sg${local.env_id_short}DatabaseVpcEndpoint"
  vpc_id = var.vpc_id

  tags = {
    Name = "databaseVpcEndpointSg"
  }
}

# Security group rules for the VPC endpoint

resource "aws_security_group_rule" "target_consumer_database_vpc_endpoint_ingress" {
  type      = "ingress"
  from_port = var.db_port
  to_port   = var.db_port
  protocol  = "tcp"

  security_group_id        = aws_security_group.database_vpc_endpoint_sg.id
  source_security_group_id = var.target_consumer_security_group_id
  description              = "Allow incoming traffic to the VPC endpoint from the target consumer"
}

resource "aws_security_group_rule" "database_vpc_endpoint_egress" {
  type        = "egress"
  from_port   = var.db_port
  to_port     = var.db_port
  protocol    = "tcp"
  cidr_blocks = ["0.0.0.0/0"]

  security_group_id = aws_security_group.database_vpc_endpoint_sg.id
  description       = "Allow outgoing traffic from the VPC endpoint to the VPC endpoint service"
}

# Security group rules for the target consumer

resource "aws_security_group_rule" "target_consumer_database_vpc_endpoint_egress" {
  type      = "egress"
  from_port = var.db_port
  to_port   = var.db_port
  protocol  = "tcp"

  security_group_id        = var.target_consumer_security_group_id
  source_security_group_id = aws_security_group.database_vpc_endpoint_sg.id
  description              = "Allow outgoing traffic to the VPC endpoint from the target consumer"
}

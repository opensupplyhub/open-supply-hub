#------------------------------------------------------------------------------
# NLB
#------------------------------------------------------------------------------

# NLB for the database proxy

resource "aws_lb" "database_proxy_nlb" {
  name = "dbProxyOsHub${var.env_identifier}Nlb"
  internal = true
  load_balancer_type = "network"
  subnets = var.subnet_ids
  enable_cross_zone_load_balancing = true
  security_groups = [aws_security_group.database_proxy_nlb_sg.id]

  tags = {
    Name = "databaseProxyNlb"
  }
}

resource "aws_lb_target_group" "database_proxy_nlb_tg" {
  name = "dbProxyOsHub${var.env_identifier}NlbTg"
  vpc_id = var.vpc_id
  port = var.db_port
  protocol = "TCP"
  target_type = "ip"

  health_check {
    protocol = "TCP"
    port = var.db_port
  }
}

resource "aws_lb_listener" "database_proxy_nlb_listener" {
  load_balancer_arn = aws_lb.database_proxy_nlb.arn
  port = var.db_port
  protocol = "TCP"
  default_action {
    type = "forward"
    target_group_arn = aws_lb_target_group.database_proxy_nlb_tg.arn
  }

  tags = {
    Name = "databaseProxyNlbListener"
  }
}

# Security group for NLB

resource "aws_security_group" "database_proxy_nlb_sg" {
  name = "sg${local.env_id_short}DbProxyNlb"
  description = "Security group for NLB"
  vpc_id = var.vpc_id

  tags = {
    Name = "databaseProxyNlbSecurityGroup"
  }
}

# Security group rules for NLB

resource "aws_security_group_rule" "nlb_proxy_egress" {
  type                     = "egress"
  from_port                = var.db_port
  to_port                  = var.db_port
  protocol                 = "tcp"

  security_group_id        = aws_security_group.database_proxy_nlb_sg.id
  source_security_group_id = aws_security_group.proxy.id
  description              = "Allow outgoing traffic from NLB to RDS proxy"
}

resource "aws_security_group_rule" "nlb_ingress" {
  type      = "ingress"
  from_port = var.db_port
  to_port = var.db_port
  protocol = "tcp"
  cidr_blocks = ["0.0.0.0/0"]

  security_group_id = aws_security_group.database_proxy_nlb_sg.id
  description = "Allow incoming traffic to NLB from anywhere"
}

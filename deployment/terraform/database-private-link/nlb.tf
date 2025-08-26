#------------------------------------------------------------------------------
# NLB
#------------------------------------------------------------------------------

locals {
  proxy_nlb_name = lower("proxy-oshub-${var.env_identifier}-nlb")
}

resource "aws_lb" "database_proxy_nlb" {
  name = local.proxy_nlb_name
  internal = true
  load_balancer_type = "network"
  subnets = var.subnet_ids
  enable_cross_zone_load_balancing = true

  tags = {
    Name = "databaseProxyNetworkLoadBalancer"
  }
}

resource "aws_lb_target_group" "database_proxy_nlb_tg" {
  name = "tgOshub${var.project_identifier}DbProxyNlb"
  vpc_id = var.vpc_id
  port = var.db_port
  protocol = "TCP"
  target_type = "ip"

  health_check {
    protocol = "TCP"
    port = var.db_port
  }
}

resource "aws_lb_target_group_attachment" "database_proxy_nlb_tg_attachment" {
    for_each = toset(var.db_proxy_ips)
    target_group_arn = aws_lb_target_group.database_proxy_nlb_tg.arn
    target_id = each.value
    port = var.db_port
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
    Name = "databaseProxyNetworkLoadBalancerListener"
  }
}

# Security group for NLB
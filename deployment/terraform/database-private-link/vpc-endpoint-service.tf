# ------------------------------------------------------------
# VPC Endpoint Service
# ------------------------------------------------------------

resource "aws_vpc_endpoint_service" "database_proxy_vpc_endpoint_service" {
  acceptance_required = false
  network_load_balancer_arns = [aws_lb.database_proxy_nlb.arn]

  tags = {
    Name = "databaseProxyVpcEndpointService"
  }
}

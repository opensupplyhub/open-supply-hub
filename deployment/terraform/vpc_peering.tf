# VPC Peering Module Integration
# This module creates VPC peering connections between environments
# to enable AWS Batch jobs to connect to RDS across VPCs

locals {
  is_requester = var.environment == var.requester_environment
  is_accepter  = var.environment == var.accepter_environment
}

module "vpc_peering" {
  source = "./vpc-peering"

  # Environment identification.
  environment         = var.environment
  is_requester        = local.is_requester
  is_accepter         = local.is_accepter

  # Current environment VPC (requester or accepter).
  requester_vpc_id                    = local.is_requester ? module.vpc.id : var.requester_vpc_id
  # requester_vpc_cidr                  = local.is_requester ? module.vpc.cidr_block : var.requester_vpc_cidr
  # requester_private_route_table_ids   = module.vpc.private_route_table_ids
  # requester_batch_security_group_id   = aws_security_group.batch.id

  # Accepter VPC configuration (for cross-environment communication).
  accepter_vpc_id                    = var.accepter_vpc_id
  # accepter_vpc_cidr                  = var.accepter_vpc_cidr
  # accepter_private_route_table_ids   = var.accepter_private_route_table_ids
  # accepter_rds_security_group_id     = var.accepter_rds_security_group_id

#   # Service configuration.
#   rds_port = 5432

#   # Feature flags.
#   create_security_group_rules = true
}

# VPC Peering Module Integration
# This module creates VPC peering connections between environments
# to enable AWS Batch jobs to connect to RDS across VPCs

module "vpc_peering" {
  source = "./vpc-peering"

  # Environment identification
  environment         = var.environment
  requester_environment = var.requester_environment
  accepter_environment  = var.accepter_environment

  # Current environment VPC (requester or accepter)
  requester_vpc_id                    = module.vpc.id
  requester_vpc_cidr                  = module.vpc.cidr_block
  requester_private_route_table_ids   = module.vpc.private_route_table_ids
  requester_batch_security_group_id   = aws_security_group.batch.id

  # Accepter VPC configuration (for cross-environment communication)
  accepter_vpc_id                    = var.accepter_vpc_id
  accepter_vpc_cidr                  = var.accepter_vpc_cidr
  accepter_private_route_table_ids   = var.accepter_private_route_table_ids
  accepter_rds_security_group_id     = var.accepter_rds_security_group_id

  # Service configuration
  rds_port = 5432

  # Feature flags
  create_security_group_rules = true
}

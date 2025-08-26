module "database_vpc_endpoint" {
  count = var.is_database_private_link_consumer ? 1 : 0

  source = "./database-vpc-endpoint"

  env_identifier = var.environment
  project_identifier = var.project
  vpc_id = module.vpc.id
  subnet_ids = module.vpc.private_subnet_ids
  vpc_endpoint_service_name = var.database_private_link_vpc_endpoint_service_name
  db_port = module.database_enc.port
  # TODO: Replace the bastion security group ID with the batch job security group ID
  target_consumer_security_group_id = module.vpc.bastion_security_group_id
}

module "database_private_link" {
  source = "./database-private-link"
  vpc_id = module.vpc.id
  subnet_ids = module.vpc.private_subnet_ids
  db_instance_identifier = var.rds_database_identifier
  env_identifier = var.environment
  project_identifier = var.project

  db_username = var.rds_database_username
  db_password = var.rds_database_password
  db_port = module.database_enc.port
  # TODO: change to NLB security group. Test with bastion first.
  allowed_security_group_id = module.vpc.bastion_security_group_id
  database_security_group_id = module.database_enc.database_security_group_id
  debug_logging = true

  db_proxy_ips = ["10.0.1.92", "10.0.3.251"]
}
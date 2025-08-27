module "database_private_link" {
  count = var.is_database_private_link_provider ? 1 : 0

  source = "./database-private-link"

  env_identifier = var.environment
  project_identifier = var.project
  vpc_id = module.vpc.id
  subnet_ids = module.vpc.private_subnet_ids
  db_instance_identifier = var.rds_database_identifier
  db_username = var.rds_database_username
  db_password = var.rds_database_password
  db_port = module.database_enc.port
  database_security_group_id = module.database_enc.database_security_group_id
  db_proxy_debug_logging = true
  db_proxy_ips = ["10.0.1.36", "10.0.3.151"]

  # TODO: Remove this variable
  bastion_security_group_id = module.vpc.bastion_security_group_id
}

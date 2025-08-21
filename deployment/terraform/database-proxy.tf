module "database_proxy" {
  source = "./database-proxy"
  vpc_id = module.vpc.id
  subnet_ids = module.vpc.private_subnet_ids
  db_instance_identifier = module.database_enc.id
  env_identifier = var.environment
  project_identifier = var.project

  db_username = var.rds_database_username
  db_password = var.rds_database_password
  # TODO: change to NLB security group. Test with bastion first.
  allowed_security_group_id = module.vpc.bastion_security_group_id
  debug_logging = true
}
module "database_private_link_provider" {
  count = var.is_database_private_link_provider ? 1 : 0

  source = "./database-private-link-provider"

  env_identifier             = var.environment
  project_identifier         = var.project
  vpc_id                     = module.vpc.id
  subnet_ids                 = module.vpc.private_subnet_ids
  db_instance_identifier     = var.rds_database_identifier
  rds_master_secret_arn      = local.rds_master_secret_arn
  db_port                    = module.database_enc.port
  database_security_group_id = module.database_enc.database_security_group_id
}

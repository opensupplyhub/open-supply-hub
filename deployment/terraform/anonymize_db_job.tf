module "database_anonymizer" {
  count = var.database_anonymizer_enabled == true ? 1 : 0

  source = "./database_anonymizer_sheduled_task"

  rds_database_identifier       = var.rds_database_identifier
  rds_database_name             = var.rds_database_name
  rds_database_username         = var.rds_database_username
  rds_database_password         = var.rds_database_password
  rds_instance_type             = var.rds_instance_type
  aws_region                    = var.aws_region
  destination_aws_account       = var.anonymizer_destination_aws_account
  anonymizer_db_identifier      = var.anonymizer_db_identifier
  database_anonymizer_image_tag = var.anonymizer_image_tag
  schedule_expression           = var.anonymizer_schedule_expression
  kms_key_admin_users           = var.anonymizer_kms_key_admin_users
  subnet_ids                    = module.vpc.private_subnet_ids
  database_subnet_group_name    = aws_db_subnet_group.default.name
  database_security_group_ids   = module.database_enc.database_security_group_id

  security_group_ids = [
    module.vpc.bastion_security_group_id,
    module.vpc.default_security_group_id
  ]
}

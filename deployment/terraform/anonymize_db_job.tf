module "database_anonymizer" {
  count = var.database_anonymizer_enabled == true ? 1 : 0

  source = "./database_anonymizer_scheduled_task"

  rds_database_identifier       = var.rds_database_identifier
  rds_database_name             = var.rds_database_name
  rds_database_username         = var.rds_database_username
  rds_database_password         = var.rds_database_password
  rds_instance_type             = var.rds_instance_type
  aws_region                    = var.aws_region
  destination_aws_account       = var.anonymizer_destination_aws_account
  anonymizer_db_identifier      = var.anonymizer_db_identifier
  database_anonymizer_image_tag = var.image_tag
  schedule_expression           = var.anonymizer_schedule_expression
  kms_key_admin_users           = var.anonymizer_kms_key_admin_users
  subnet_ids                    = module.vpc.private_subnet_ids
  database_subnet_group_name    = aws_db_subnet_group.default.name
  database_security_group_ids   = module.database_enc.database_security_group_id
  environment                   = var.environment

  security_group_ids = [
    module.vpc.bastion_security_group_id,
    module.vpc.default_security_group_id
  ]
}

module "anonymized_database_dump" {
  count = var.anonymized_database_dump_enabled == true ? 1 : 0

  source = "./anonymized_database_dump_scheduled_task"

  anonymized_database_name                 = var.anonymized_database_name
  anonymized_database_username             = var.anonymized_database_username
  anonymized_database_password             = var.anonymized_database_password
  anonymized_database_instance_type        = var.anonymized_database_instance_type
  aws_region                               = var.aws_region
  anonymized_database_identifier           = var.anonymized_database_identifier
  anonymized_database_dump_image_tag       = var.image_tag
  anonymized_database_schedule_expression  = var.anonymized_database_schedule_expression
  anonymized_database_kms_key_id           = var.anonymized_database_kms_key_id
  anonymized_database_subnet_ids           = module.vpc.private_subnet_ids
  anonymized_database_subnet_group_name    = aws_db_subnet_group.default.name
  environment                              = var.environment

  anonymized_database_security_group_ids = [
    module.vpc.default_security_group_id
  ]
}

#
# RDS resources
#
resource "aws_db_subnet_group" "default" {
  name        = replace(var.rds_database_identifier, "-enc", "")
  description = "Private subnets for the RDS instances"

  subnet_ids = module.vpc.private_subnet_ids

  tags = {
    Name        = "dbsngDatabaseServer"
    Project     = var.project
    Environment = var.environment
  }
}

resource "aws_db_parameter_group" "default" {
  name_prefix = replace(var.rds_database_identifier, "-enc", "")
  description = "Parameter group for the RDS instances"
  family      = var.rds_parameter_group_family

  parameter {
    name  = "seq_page_cost"
    value = var.rds_seq_page_cost
  }

  parameter {
    name  = "random_page_cost"
    value = var.rds_random_page_cost
  }

  parameter {
    name  = "log_min_duration_statement"
    value = var.rds_log_min_duration_statement
  }

  parameter {
    name  = "log_connections"
    value = var.rds_log_connections
  }

  parameter {
    name  = "log_disconnections"
    value = var.rds_log_disconnections
  }

  parameter {
    name  = "log_lock_waits"
    value = var.rds_log_lock_waits
  }

  parameter {
    name  = "log_temp_files"
    value = var.rds_log_temp_files
  }

  parameter {
    name  = "log_autovacuum_min_duration"
    value = var.rds_log_autovacuum_min_duration
  }

  parameter {
    name  = "work_mem"
    value = var.rds_work_mem
  }

  # pgaudit must be present in shared_preload_libraries so that the extension is
  # loaded at server start. This is a static parameter, so the change only takes
  # effect after the instance is rebooted -- hence apply_method =
  # "pending-reboot". pg_stat_statements is loaded by default on PostgreSQL 11
  # and later, and is listed explicitly here so that overriding this parameter
  # does not silently drop it.
  parameter {
    name         = "shared_preload_libraries"
    value        = var.rds_shared_preload_libraries
    apply_method = "pending-reboot"
  }

  # Classes of SQL statements that pgaudit records. Deliberately "none" for now:
  # CREATE EXTENSION pgaudit installs the event triggers that supply object type
  # and object name for DDL records, and it can only run once the library above
  # is loaded at server start. Setting a real class before that would produce
  # DDL records naming no object. Phase 2 (OSDEV-3236) flips the default to
  # "ddl,role" once the extension exists in every environment -- see
  # doc/ops/database-auditing.md.
  parameter {
    name         = "pgaudit.log"
    value        = var.rds_pgaudit_log
    apply_method = "pending-reboot"
  }

  tags = {
    Name        = "dbpgDatabaseServer"
    Project     = var.project
    Environment = var.environment
  }

  lifecycle {
    create_before_destroy = true
  }
}

module "database_enc" {
  source = "github.com/opensupplyhub/terraform-aws-postgresql-rds?ref=3.3.0"

  vpc_id                      = module.vpc.id
  allocated_storage           = var.rds_allocated_storage
  engine_version              = var.rds_engine_version
  instance_type               = var.rds_instance_type
  storage_type                = var.rds_storage_type
  iops                        = var.rds_iops
  database_identifier         = var.rds_database_identifier
  database_name               = var.rds_database_name
  database_username           = local.rds_database_username
  database_password           = local.rds_database_password
  backup_retention_period     = var.rds_backup_retention_period
  backup_window               = var.rds_backup_window
  maintenance_window          = var.rds_maintenance_window
  auto_minor_version_upgrade  = var.rds_auto_minor_version_upgrade
  allow_major_version_upgrade = var.rds_allow_major_version_upgrade
  apply_immediately           = var.rds_apply_immediately
  final_snapshot_identifier   = join("-", [var.rds_final_snapshot_identifier, formatdate("YYYYMMDDhhmmss", timestamp())])
  skip_final_snapshot         = var.rds_skip_final_snapshot
  copy_tags_to_snapshot       = var.rds_copy_tags_to_snapshot
  multi_availability_zone     = var.rds_multi_az
  storage_encrypted           = var.rds_storage_encrypted
  subnet_group                = aws_db_subnet_group.default.name
  parameter_group             = aws_db_parameter_group.default.name
  deletion_protection         = var.rds_deletion_protection
  snapshot_identifier         = var.snapshot_identifier

  alarm_cpu_threshold                  = var.rds_cpu_threshold_percent
  alarm_disk_queue_threshold           = var.rds_disk_queue_threshold
  alarm_free_disk_threshold            = var.rds_free_disk_threshold_bytes
  alarm_free_memory_threshold          = var.rds_free_memory_threshold_bytes
  alarm_cpu_credit_balance_threshold   = var.rds_cpu_credit_balance_threshold
  alarm_database_connections_threshold = var.rds_database_connections_alarm_threshold
  alarm_actions                        = [aws_sns_topic.global.arn]
  ok_actions                           = [aws_sns_topic.global.arn]
  insufficient_data_actions            = [aws_sns_topic.global.arn]

  project     = var.project
  environment = var.environment
}


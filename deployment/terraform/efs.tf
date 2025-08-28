# EFS for Logstash

resource "aws_efs_file_system" "efs_app_logstash" {
  creation_token = "${lower(replace(var.project, " ", ""))}-${lower(var.environment)}-efs-app-logstash"

  tags = {
    Name         = "efsAppLogstash"
    Project      = var.project
    Environment  = var.environment
  }
}

resource "aws_security_group" "efs_app_logstash" {
  vpc_id = module.vpc.id

  tags = {
    Name        = "sgEfsAppLogstash"
    Project     = var.project
    Environment = var.environment
  }
}

resource "aws_security_group_rule" "efs_app_logstash_ingress" {
  type             = "ingress"
  from_port        = 2049
  to_port          = 2049
  protocol         = "tcp"

  security_group_id        = aws_security_group.efs_app_logstash.id
  source_security_group_id = aws_security_group.app_logstash.id
}

resource "aws_efs_mount_target" "efs_app_logstash" {
  count           = length(module.vpc.private_subnet_ids)
  file_system_id  = aws_efs_file_system.efs_app_logstash.id
  subnet_id       = module.vpc.private_subnet_ids[count.index]
  security_groups = [aws_security_group.efs_app_logstash.id]
}

# Set EFS access point permissions for the logstash:root user.
resource "aws_efs_access_point" "efs_app_logstash_user" {
  file_system_id = aws_efs_file_system.efs_app_logstash.id
  posix_user {
    gid = 0
    uid = 1000
  }

  root_directory {
    path = "/logstash"
    creation_info {
      owner_uid = 1000
      owner_gid = 0
      permissions = 755
    }
  }

  tags = {
    Name        = "sgEfsAppLogstashAccessPointUser"
    Project     = var.project
    Environment = var.environment
  }
}

# EFS for Database Sync Timestamps

resource "aws_efs_file_system" "efs_db_sync" {
  count = var.environment == "Rba" ? 1 : 0

  creation_token = "${lower(replace(var.project, " ", ""))}-${lower(var.environment)}-efs-db-sync"

  tags = {
    Name         = "efsDbSync"
    Project      = var.project
    Environment  = var.environment
  }
}

resource "aws_security_group" "efs_db_sync" {
  count = var.environment == "Rba" ? 1 : 0

  vpc_id = module.vpc.id

  tags = {
    Name        = "sgEfsDbSync"
    Project     = var.project
    Environment = var.environment
  }
}

resource "aws_security_group_rule" "efs_db_sync_ingress" {
  count = var.environment == "Rba" ? 1 : 0

  type             = "ingress"
  from_port        = 2049
  to_port          = 2049
  protocol         = "tcp"

  security_group_id        = aws_security_group.efs_db_sync[0].id
  source_security_group_id = aws_security_group.batch.id
}

resource "aws_efs_mount_target" "efs_db_sync" {
  count = contains(["Rba", "Preprod"], var.environment) ? length(module.vpc.private_subnet_ids) : 0

  file_system_id  = aws_efs_file_system.efs_db_sync[0].id
  subnet_id       = module.vpc.private_subnet_ids[count.index]
  security_groups = [aws_security_group.efs_db_sync[0].id]
}

# Set EFS access point permissions for database sync batch jobs
resource "aws_efs_access_point" "efs_db_sync_user" {
  count = var.environment == "Rba" ? 1 : 0

  file_system_id = aws_efs_file_system.efs_db_sync[0].id
  posix_user {
    gid = 0
    uid = 1000
  }

  root_directory {
    path = "/db-sync"
    creation_info {
      owner_uid = 1000
      owner_gid = 0
      permissions = 755
    }
  }

  tags = {
    Name        = "sgEfsDbSyncAccessPointUser"
    Project     = var.project
    Environment = var.environment
  }
}

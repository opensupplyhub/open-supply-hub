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

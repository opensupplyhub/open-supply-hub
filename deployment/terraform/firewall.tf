#
# Bastion security group resources
#
resource "aws_security_group_rule" "bastion_ssh_ingress" {
  type        = "ingress"
  from_port   = 22
  to_port     = 22
  protocol    = "tcp"
  cidr_blocks = var.external_access_cidr_blocks

  security_group_id = module.vpc.bastion_security_group_id
}

resource "aws_security_group_rule" "bastion_ssh_egress" {
  type      = "egress"
  from_port = 22
  to_port   = 22
  protocol  = "tcp"

  cidr_blocks = [module.vpc.cidr_block]

  security_group_id = module.vpc.bastion_security_group_id
}

resource "aws_security_group_rule" "bastion_rds_enc_egress" {
  type      = "egress"
  from_port = module.database_enc.port
  to_port   = module.database_enc.port
  protocol  = "tcp"

  security_group_id        = module.vpc.bastion_security_group_id
  source_security_group_id = module.database_enc.database_security_group_id
}

resource "aws_security_group_rule" "bastion_app_egress" {
  type      = "egress"
  from_port = var.app_port
  to_port   = var.app_port
  protocol  = "tcp"

  security_group_id        = module.vpc.bastion_security_group_id
  source_security_group_id = aws_security_group.app.id
}

resource "aws_security_group_rule" "bastion_app_cc_egress" {
  type      = "egress"
  from_port = var.app_cc_port
  to_port   = var.app_cc_port
  protocol  = "tcp"

  security_group_id        = module.vpc.bastion_security_group_id
  source_security_group_id = aws_security_group.app.id
}

resource "aws_security_group_rule" "bastion_http_egress" {
  type             = "egress"
  from_port        = "80"
  to_port          = "80"
  protocol         = "tcp"
  cidr_blocks      = ["0.0.0.0/0"]
  ipv6_cidr_blocks = ["::/0"]

  security_group_id = module.vpc.bastion_security_group_id
}

resource "aws_security_group_rule" "bastion_https_egress" {
  type             = "egress"
  from_port        = "443"
  to_port          = "443"
  protocol         = "tcp"
  cidr_blocks      = ["0.0.0.0/0"]
  ipv6_cidr_blocks = ["::/0"]

  security_group_id = module.vpc.bastion_security_group_id
}

resource "aws_security_group_rule" "bastion_memcached_egress" {
  type      = "egress"
  from_port = var.ec_memcached_port
  to_port   = var.ec_memcached_port
  protocol  = "tcp"

  security_group_id        = module.vpc.bastion_security_group_id
  source_security_group_id = aws_security_group.memcached.id
}

#
# App ALB security group resources
#
resource "aws_security_group_rule" "alb_https_ingress" {
  type             = "ingress"
  from_port        = 443
  to_port          = 443
  protocol         = "tcp"
  cidr_blocks      = ["0.0.0.0/0"]
  ipv6_cidr_blocks = ["::/0"]

  security_group_id = aws_security_group.alb.id
}

resource "aws_security_group_rule" "alb_app_egress" {
  type      = "egress"
  from_port = var.app_port
  to_port   = var.app_port
  protocol  = "tcp"

  security_group_id        = aws_security_group.alb.id
  source_security_group_id = aws_security_group.app.id
}

resource "aws_security_group_rule" "alb_app_cc_egress" {
  type      = "egress"
  from_port = var.app_cc_port
  to_port   = var.app_cc_port
  protocol  = "tcp"

  security_group_id        = aws_security_group.alb.id
  source_security_group_id = aws_security_group.app_cc.id
}


#
# RDS security group resources
#
resource "aws_security_group_rule" "rds_enc_app_ingress" {
  type      = "ingress"
  from_port = module.database_enc.port
  to_port   = module.database_enc.port
  protocol  = "tcp"

  security_group_id        = module.database_enc.database_security_group_id
  source_security_group_id = aws_security_group.app.id
}


resource "aws_security_group_rule" "rds_enc_batch_ingress" {
  type      = "ingress"
  from_port = module.database_enc.port
  to_port   = module.database_enc.port
  protocol  = "tcp"

  security_group_id        = module.database_enc.database_security_group_id
  source_security_group_id = aws_security_group.batch.id
}

resource "aws_security_group_rule" "rds_enc_bastion_ingress" {
  type      = "ingress"
  from_port = module.database_enc.port
  to_port   = module.database_enc.port
  protocol  = "tcp"

  security_group_id        = module.database_enc.database_security_group_id
  source_security_group_id = module.vpc.bastion_security_group_id
}

resource "aws_security_group_rule" "rds_enc_app_logstash_ingress" {
  type      = "ingress"
  from_port = module.database_enc.port
  to_port   = module.database_enc.port
  protocol  = "tcp"

  security_group_id        = module.database_enc.database_security_group_id
  source_security_group_id = aws_security_group.app_logstash.id
}

#
# Memcached security group resources
#
resource "aws_security_group_rule" "memcached_app_ingress" {
  type      = "ingress"
  from_port = var.ec_memcached_port
  to_port   = var.ec_memcached_port
  protocol  = "tcp"

  security_group_id        = aws_security_group.memcached.id
  source_security_group_id = aws_security_group.app.id
}

resource "aws_security_group_rule" "memcached_batch_ingress" {
  type      = "ingress"
  from_port = var.ec_memcached_port
  to_port   = var.ec_memcached_port
  protocol  = "tcp"

  security_group_id        = aws_security_group.memcached.id
  source_security_group_id = aws_security_group.batch.id
}

resource "aws_security_group_rule" "memcached_bastion_ingress" {
  type      = "ingress"
  from_port = var.ec_memcached_port
  to_port   = var.ec_memcached_port
  protocol  = "tcp"

  security_group_id        = aws_security_group.memcached.id
  source_security_group_id = module.vpc.bastion_security_group_id
}

#
# ECS container instance security group resources
#
resource "aws_security_group_rule" "app_https_egress" {
  type             = "egress"
  from_port        = 443
  to_port          = 443
  protocol         = "tcp"
  cidr_blocks      = ["0.0.0.0/0"]
  ipv6_cidr_blocks = ["::/0"]

  security_group_id = aws_security_group.app.id
}

resource "aws_security_group_rule" "app_https_egress_local" {
  type        = "egress"
  from_port   = 0
  to_port     = 65535
  protocol    = "tcp"
  cidr_blocks = [module.vpc.cidr_block]

  security_group_id = aws_security_group.app.id
}

resource "aws_security_group_rule" "app_cc_https_egress" {
  type             = "egress"
  from_port        = 443
  to_port          = 443
  protocol         = "tcp"
  cidr_blocks      = ["0.0.0.0/0"]
  ipv6_cidr_blocks = ["::/0"]

  security_group_id = aws_security_group.app_cc.id
}

resource "aws_security_group_rule" "app_cc_http_egress" {
  type             = "egress"
  from_port        = 80
  to_port          = 80
  protocol         = "tcp"
  cidr_blocks      = [module.vpc.cidr_block]
  ipv6_cidr_blocks = ["::/0"]

  security_group_id = aws_security_group.app_cc.id
}

resource "aws_security_group_rule" "app_cc_http_egress_local" {
  type        = "egress"
  from_port   = 0
  to_port     = 65535
  protocol    = "tcp"
  cidr_blocks = [module.vpc.cidr_block]

  security_group_id = aws_security_group.app_cc.id
}

resource "aws_security_group_rule" "app_rds_enc_egress" {
  type      = "egress"
  from_port = module.database_enc.port
  to_port   = module.database_enc.port
  protocol  = "tcp"

  security_group_id        = aws_security_group.app.id
  source_security_group_id = module.database_enc.database_security_group_id
}

resource "aws_security_group_rule" "app_opensearch_egress" {
  type      = "egress"
  from_port = var.opensearch_port
  to_port   = var.opensearch_port
  protocol  = "tcp"

  security_group_id        = aws_security_group.app.id
  source_security_group_id = aws_security_group.opensearch.id
}

resource "aws_security_group_rule" "batch_opensearch_egress" {
  type      = "egress"
  from_port = var.opensearch_port
  to_port   = var.opensearch_port
  protocol  = "tcp"

  security_group_id        = aws_security_group.batch.id
  source_security_group_id = aws_security_group.opensearch.id
}

resource "aws_security_group_rule" "app_alb_ingress" {
  type      = "ingress"
  from_port = var.app_port
  to_port   = var.app_port
  protocol  = "tcp"

  security_group_id        = aws_security_group.app.id
  source_security_group_id = aws_security_group.alb.id
}

resource "aws_security_group_rule" "app_ingress_local" {
  type      = "ingress"
  from_port = var.app_port
  to_port   = var.app_port
  protocol  = "tcp"

  security_group_id        = aws_security_group.app.id
  source_security_group_id = aws_security_group.app_cc.id
}

resource "aws_security_group_rule" "app_bastion_ingress" {
  type      = "ingress"
  from_port = var.app_port
  to_port   = var.app_port
  protocol  = "tcp"

  security_group_id        = aws_security_group.app.id
  source_security_group_id = module.vpc.bastion_security_group_id
}

resource "aws_security_group_rule" "app_cc_alb_ingress" {
  type      = "ingress"
  from_port = var.app_cc_port
  to_port   = var.app_cc_port
  protocol  = "tcp"

  security_group_id        = aws_security_group.app_cc.id
  source_security_group_id = aws_security_group.alb.id
}

resource "aws_security_group_rule" "app_cc_bastion_ingress" {
  type      = "ingress"
  from_port = var.app_cc_port
  to_port   = var.app_cc_port
  protocol  = "tcp"

  security_group_id        = aws_security_group.app_cc.id
  source_security_group_id = module.vpc.bastion_security_group_id
}

resource "aws_security_group_rule" "app_memcached_egress" {
  type      = "egress"
  from_port = var.ec_memcached_port
  to_port   = var.ec_memcached_port
  protocol  = "tcp"

  security_group_id        = aws_security_group.app.id
  source_security_group_id = aws_security_group.memcached.id
}

resource "aws_security_group_rule" "app_logstash_egress" {
  type      = "egress"
  from_port = module.database_enc.port
  to_port   = module.database_enc.port
  protocol  = "tcp"

  security_group_id        = aws_security_group.app_logstash.id
  source_security_group_id = module.database_enc.database_security_group_id
}

resource "aws_security_group_rule" "app_logstash_opensearch_egress" {
  type      = "egress"
  from_port = var.opensearch_port
  to_port   = var.opensearch_port
  protocol  = "tcp"

  security_group_id        = aws_security_group.app_logstash.id
  source_security_group_id = aws_security_group.opensearch.id
}

resource "aws_security_group_rule" "app_logstash_https_egress" {
  type             = "egress"
  from_port        = 443
  to_port          = 443
  protocol         = "tcp"
  cidr_blocks      = ["0.0.0.0/0"]
  ipv6_cidr_blocks = ["::/0"]

  security_group_id = aws_security_group.app_logstash.id
}

resource "aws_security_group_rule" "app_logstash_efs_egress" {
  type      = "egress"
  from_port = 2049
  to_port   = 2049
  protocol  = "tcp"

  security_group_id        = aws_security_group.app_logstash.id
  source_security_group_id = aws_security_group.efs_app_logstash.id
}

#
# Batch container instance security group resources
#
resource "aws_security_group_rule" "batch_https_egress" {
  type        = "egress"
  from_port   = 443
  to_port     = 443
  protocol    = "tcp"
  cidr_blocks = ["0.0.0.0/0"]

  security_group_id = aws_security_group.batch.id
}

resource "aws_security_group_rule" "batch_rds_enc_egress" {
  type      = "egress"
  from_port = module.database_enc.port
  to_port   = module.database_enc.port
  protocol  = "tcp"

  security_group_id        = aws_security_group.batch.id
  source_security_group_id = module.database_enc.database_security_group_id
}

resource "aws_security_group_rule" "batch_bastion_ingress" {
  type      = "ingress"
  from_port = 22
  to_port   = 22
  protocol  = "tcp"

  security_group_id        = aws_security_group.batch.id
  source_security_group_id = module.vpc.bastion_security_group_id
}

resource "aws_security_group_rule" "batch_memcached_egress" {
  type      = "egress"
  from_port = var.ec_memcached_port
  to_port   = var.ec_memcached_port
  protocol  = "tcp"

  security_group_id        = aws_security_group.batch.id
  source_security_group_id = aws_security_group.memcached.id
}

resource "aws_security_group_rule" "batch_msk_egress" {
  type      = "egress"
  from_port = 9092
  to_port   = 9092
  protocol  = "tcp"

  security_group_id        = aws_security_group.batch.id
  source_security_group_id = aws_security_group.msk.id
}

resource "aws_security_group_rule" "batch_db_sync_egress" {
  count = contains(["Rba", "Preprod"], var.environment) ? 1 : 0

  type      = "egress"
  from_port = 2049
  to_port   = 2049
  protocol  = "tcp"

  security_group_id        = aws_security_group.batch.id
  source_security_group_id = aws_security_group.efs_db_sync[0].id
}

resource "aws_security_group_rule" "logstash_opensearch_ingress" {
  type      = "ingress"
  from_port = var.opensearch_port
  to_port   = var.opensearch_port
  protocol  = "tcp"

  security_group_id        = aws_security_group.opensearch.id
  source_security_group_id = aws_security_group.app_logstash.id
}

resource "aws_security_group_rule" "app_opensearch_ingress" {
  type      = "ingress"
  from_port = var.opensearch_port
  to_port   = var.opensearch_port
  protocol  = "tcp"

  security_group_id        = aws_security_group.opensearch.id
  source_security_group_id = aws_security_group.app.id
}


resource "aws_security_group_rule" "batch_opensearch_ingress" {
  type      = "ingress"
  from_port = var.opensearch_port
  to_port   = var.opensearch_port
  protocol  = "tcp"

  security_group_id        = aws_security_group.opensearch.id
  source_security_group_id = aws_security_group.batch.id
}

resource "aws_security_group_rule" "bastion_opensearch_ingress" {
  type      = "ingress"
  from_port = var.opensearch_port
  to_port   = var.opensearch_port
  protocol  = "tcp"

  security_group_id        = aws_security_group.opensearch.id
  source_security_group_id = module.vpc.bastion_security_group_id
}

resource "aws_security_group_rule" "bastion_efs_ingress" {
  type      = "ingress"
  from_port = 2049
  to_port   = 2049
  protocol  = "tcp"

  security_group_id        = aws_security_group.efs_app_logstash.id
  source_security_group_id = module.vpc.bastion_security_group_id
}

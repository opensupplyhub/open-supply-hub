module "msk_cluster" {
  source  = "terraform-aws-modules/msk-kafka-cluster/aws"
  version = "2.1.0"

  name                   = "${lower(replace(var.project, " ", ""))}-${lower(var.environment)}-msk"
  kafka_version          = "3.9.x"
  create_configuration   = false
  configuration_arn      = aws_msk_configuration.msk_config.arn
  configuration_revision = aws_msk_configuration.msk_config.latest_revision
  number_of_broker_nodes = 2
  encryption_in_transit_client_broker = "PLAINTEXT"
  encryption_in_transit_in_cluster = "false"

  broker_node_client_subnets  = module.vpc.private_subnet_ids
  broker_node_instance_type   = "kafka.t3.small"
  broker_node_security_groups = [aws_security_group.msk.id]
}

# Keep the current MSK configuration referenced intentionally; remove when no longer needed.
resource "aws_msk_configuration" "msk_config" {
  name           = "${lower(replace(var.project, " ", ""))}-${lower(var.environment)}-msk"
  kafka_versions = ["3.4.0", "3.9.x"]
  # With 2 brokers (2 AZs), RF=2 with MinISR=1 is the highest-availability
  # option: MinISR must stay below RF so a single broker failure or rolling
  # MSK update doesn't block producers using acks=all.
  #
  # These are cluster DEFAULTS only - they do not apply to a topic that sets its
  # own min.insync.replicas. Topic-level overrides are repaired separately by
  # src/kafka-tools/fix_replication.sh, which must be run before this
  # configuration revision is applied (applying it triggers a rolling broker
  # restart, the exact failure window the advisory describes). See OSDEV-3063.
  server_properties = <<-EOT
    default.replication.factor=2
    min.insync.replicas=1
  EOT

  lifecycle {
    prevent_destroy = false
    ignore_changes = [
      kafka_versions,
    ]
  }
}

resource "aws_security_group" "msk" {
  vpc_id = module.vpc.id

  tags = {
    Name        = "sgMSKCluster"
    Project     = var.project
    Environment = var.environment
  }
}

resource "aws_security_group_rule" "msk_inbount" {
  type      = "ingress"
  from_port = 0
  to_port   = 65535
  protocol  = "tcp"
  cidr_blocks = ["0.0.0.0/0"]

  security_group_id = aws_security_group.msk.id
}

resource "aws_security_group_rule" "msk_outbound" {
  type      = "egress"
  from_port = 0
  to_port   = 65535
  protocol  = "tcp"
  cidr_blocks = ["0.0.0.0/0"]

  security_group_id = aws_security_group.msk.id
}
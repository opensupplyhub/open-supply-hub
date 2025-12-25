module "msk_cluster" {
  source  = "terraform-aws-modules/msk-kafka-cluster/aws"
  version = "2.1.0"

  name                   = "${lower(replace(var.project, " ", ""))}-${lower(var.environment)}-msk"
  kafka_version          = "3.9.0"
  number_of_broker_nodes = 2
  encryption_in_transit_client_broker = "PLAINTEXT"
  encryption_in_transit_in_cluster = "false"

  broker_node_client_subnets  = module.vpc.private_subnet_ids
  broker_node_instance_type   = "kafka.t3.small"
  broker_node_security_groups = [aws_security_group.msk.id]
}

# Keep the current MSK configuration referenced so Terraform won't delete it;
# safe to remove once the cluster is on 3.9.x and a matching config is managed.
resource "aws_msk_configuration" "msk_config" {
  name            = "${lower(replace(var.project, " ", ""))}-${lower(var.environment)}-msk"
  kafka_versions  = ["3.4.0"]
  server_properties = ""

  lifecycle {
    prevent_destroy = true
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

# locals {
#   broker_host_list = "${split(",", replace(element(concat(module.msk_cluster.bootstrap_brokers, list("")), 0), ":9092", ""))}"
# }



# locals {
#   broker_host_list = split(",",module.msk_cluster.bootstrap_brokers[0])
# }


# provider "kafka" {
#   # bootstrap_servers = ["${module.msk_cluster.bootstrap_brokers}"]
#   # bootstrap_servers = module.msk_cluster.bootstrap_brokers
#   bootstrap_servers = local.broker_host_list
# }

# resource "kafka_topic" "logs" {
#   # bootstrap_servers = join(",", module.msk_cluster.bootstrap_brokers)
#   name               = "${var.topic_dedup_basic_name}"
#   replication_factor = 1
#   partitions         = 1
# }
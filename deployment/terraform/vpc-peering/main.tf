# Get VPC peering connection for accepter environment.
# data "aws_vpc_peering_connections" "accepter_peering" {
#   count = var.is_accepter ? 1 : 0
  
#   filter {
#     name   = "accepter-vpc-id"
#     values = [var.accepter_vpc_id]
#   }
  
#   filter {
#     name   = "requester-vpc-id"
#     values = [var.requester_vpc_id]
#   }
  
#   filter {
#     name   = "status"
#     values = ["active"]
#   }
# }

# VPC Peering Connection.
resource "aws_vpc_peering_connection" "to_accepter" {
  count = var.is_requester ? 1 : 0

  vpc_id      = var.requester_vpc_id
  peer_vpc_id = var.accepter_vpc_id

  # Same account allows auto-accept.
  auto_accept = true

  tags = {
    Name        = "${var.environment}-to-accepter-peering"
  }
}

# # Route table entries for requester VPC.
# resource "aws_route" "requester_to_accepter" {
#   count = var.is_requester ? length(var.requester_private_route_table_ids) : 0

#   route_table_id            = var.requester_private_route_table_ids[count.index]
#   destination_cidr_block    = var.accepter_vpc_cidr
#   vpc_peering_connection_id = aws_vpc_peering_connection.to_accepter[0].id

#   depends_on = [aws_vpc_peering_connection.to_accepter]
# }

# # Route table entries for accepter VPC.
# resource "aws_route" "accepter_to_requester" {
#   count = var.is_accepter ? length(var.accepter_private_route_table_ids) : 0

#   route_table_id            = var.accepter_private_route_table_ids[count.index]
#   destination_cidr_block    = var.requester_vpc_cidr
#   vpc_peering_connection_id = data.aws_vpc_peering_connections.accepter_peering[0].ids[0]
# }

# # Security Group Rule: Allow Batch jobs from requester to connect to RDS in accepter.
# resource "aws_security_group_rule" "accepter_rds_from_requester" {
#   count = var.is_requester ? 1 : 0

#   depends_on = [aws_vpc_peering_connection.to_accepter]

#   type      = "ingress"
#   from_port = var.rds_port
#   to_port   = var.rds_port
#   protocol  = "tcp"

#   security_group_id        = var.accepter_rds_security_group_id
#   source_security_group_id = var.requester_batch_security_group_id

#   description = "Allow ${var.environment} batch jobs to connect to accepter RDS"
# }

# # Security Group Rule: Allow requester batch security group to send traffic to accepter.
# resource "aws_security_group_rule" "requester_batch_to_accepter" {
#   count = var.is_requester ? 1 : 0

#   depends_on = [aws_vpc_peering_connection.to_accepter]

#   type      = "egress"
#   from_port = var.rds_port
#   to_port   = var.rds_port
#   protocol  = "tcp"

#   security_group_id        = var.requester_batch_security_group_id
#   source_security_group_id = var.accepter_rds_security_group_id

#   description = "Allow ${var.environment} batch jobs to send traffic to accepter RDS"
# }

# # Validation: Ensure VPC CIDRs don't overlap.
# resource "null_resource" "validate_cidr_overlap" {
#   count = var.is_requester ? 1 : 0

#   lifecycle {
#     precondition {
#       condition     = var.requester_vpc_cidr != var.accepter_vpc_cidr
#       error_message = "Requester and accepter VPC CIDRs cannot be the same"
#     }
#   }
# }

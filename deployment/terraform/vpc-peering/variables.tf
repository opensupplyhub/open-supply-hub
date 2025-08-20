variable "environment" {
  description = "The current environment being deployed (e.g., 'Production', 'Rba')."
  type        = string
}

variable "is_requester" {
  description = "Whether the current environment is the requester."
  type        = bool
}

variable "is_accepter" {
  description = "Whether the current environment is the accepter."
  type        = bool
}

# Requester VPC Configuration
variable "requester_vpc_id" {
  description = "VPC ID of the requester environment (needed for accepter environment to find peering connection)."
  type        = string
  default     = null
}

# variable "requester_vpc_cidr" {
#   description = "CIDR block of the requester VPC"
#   type        = string
#   default     = null
# }

# variable "requester_private_route_table_ids" {
#   description = "List of private route table IDs in the requester VPC"
#   type        = list(string)
#   default     = []
# }

# variable "requester_batch_security_group_id" {
#   description = "Security group ID of the batch jobs in the requester VPC"
#   type        = string
#   default     = null
# }

# Accepter VPC Configuration
variable "accepter_vpc_id" {
  description = "VPC ID of the accepter environment"
  type        = string
  default     = null
}

# variable "accepter_vpc_cidr" {
#   description = "CIDR block of the accepter VPC"
#   type        = string
#   default     = null
# }

# variable "accepter_private_route_table_ids" {
#   description = "List of private route table IDs in the accepter VPC"
#   type        = list(string)
#   default     = []
# }

# variable "accepter_rds_security_group_id" {
#   description = "Security group ID of the RDS instance in the accepter VPC"
#   type        = string
#   default     = null
# }

# # VPC Peering Connection ID (for accepter environment to reference)
# variable "vpc_peering_connection_id" {
#   description = "ID of the VPC peering connection to use for routing (needed for accepter environment)"
#   type        = string
#   default     = null
# }

# # Service Configuration
# variable "rds_port" {
#   description = "Port number for RDS PostgreSQL (default: 5432)"
#   type        = number
#   default     = 5432
# }

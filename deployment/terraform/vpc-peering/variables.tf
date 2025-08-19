variable "environment" {
  description = "The current environment being deployed (e.g., 'Production', 'Rba')"
  type        = string
}

variable "requester_environment" {
  description = "The name of the environment that will be the requester (e.g., 'Rba')"
  type        = string
}

variable "accepter_environment" {
  description = "The name of the environment that will be the accepter (e.g., 'Production')"
  type        = string
}

# Requester VPC Configuration
variable "requester_vpc_id" {
  description = "VPC ID of the requester environment"
  type        = string
  default     = null
}

variable "requester_vpc_cidr" {
  description = "CIDR block of the requester VPC"
  type        = string
  default     = null
}

variable "requester_private_route_table_ids" {
  description = "List of private route table IDs in the requester VPC"
  type        = list(string)
  default     = []
}

variable "requester_batch_security_group_id" {
  description = "Security group ID of the batch jobs in the requester VPC"
  type        = string
  default     = null
}

# Accepter VPC Configuration
variable "accepter_vpc_id" {
  description = "VPC ID of the accepter environment"
  type        = string
  default     = null
}

variable "accepter_vpc_cidr" {
  description = "CIDR block of the accepter VPC"
  type        = string
  default     = null
}

variable "accepter_private_route_table_ids" {
  description = "List of private route table IDs in the accepter VPC"
  type        = list(string)
  default     = []
}

variable "accepter_rds_security_group_id" {
  description = "Security group ID of the RDS instance in the accepter VPC"
  type        = string
  default     = null
}

# Service Configuration
variable "rds_port" {
  description = "Port number for RDS PostgreSQL (default: 5432)"
  type        = number
  default     = 5432
}

# Feature Flags
variable "create_security_group_rules" {
  description = "Whether to create security group rules for cross-VPC communication"
  type        = bool
  default     = true
}

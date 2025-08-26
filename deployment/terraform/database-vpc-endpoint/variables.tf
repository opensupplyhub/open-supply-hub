variable "env_identifier" {
  type        = string
  description = "Environment identifier"
}

variable "project_identifier" {
  type        = string
  description = "Project identifier"
}

variable "vpc_id" {
  type        = string
  description = "VPC ID of the VPC where the VPC endpoint will be created"
}

variable "subnet_ids" {
  type        = list(string)
  description = "Subnet IDs of the VPC where the VPC endpoint will be created"
}

variable "vpc_endpoint_service_name" {
  type        = string
  description = "The name of the VPC endpoint service in the provider VPC"
}

# Database configuration

variable "db_port" {
  type        = number
  description = "Port of the database"
}

# Target consumer configuration

variable "target_consumer_security_group_id" {
  type        = string
  description = "Security group ID of the target consumer"
}

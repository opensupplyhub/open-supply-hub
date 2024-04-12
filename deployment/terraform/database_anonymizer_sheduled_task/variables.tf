variable "rds_database_identifier" {
}

variable "rds_database_name" {
}

variable "rds_database_username" {
}

variable "rds_database_password" {
  sensitive = true
}

variable "destination_aws_account" {
  type = string
}
variable "anonymizer_db_identifier" {
  type = string
}

variable "project" {
  default = "Open Supply Hub"
}

variable "environment" {
  default = "Staging"
}

variable "database_anonymizer_image_tag" {
  type    = string
  default = "latest"
}

variable "aws_region" {
  type    = string
  default = "eu-west-1"
}

variable "subnet_ids" {
  type = list(string)
}

variable "security_group_ids" {
  type = list(string)
}

variable "schedule_expression" {
  type = string
}

variable "rds_instance_type" {
  type = string
}

variable "database_subnet_group_name" {
  type = string
}

variable "database_security_group_ids" {
  type = string
}

variable "kms_key_admin_users" {
  type    = list(any)
  default = []
}

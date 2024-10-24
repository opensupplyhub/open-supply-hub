variable "anonymized_database_identifier" {
}

variable "anonymized_database_name" {
}

variable "anonymized_database_username" {
}

variable "anonymized_database_password" {
  sensitive = true
}

variable "project" {
  default = "Open Supply Hub"
}

variable "environment" {
  default = "Staging"
}

variable "anonymized_database_dump_image_tag" {
  type    = string
  default = "latest"
}

variable "aws_region" {
  type    = string
  default = "eu-west-1"
}

variable "anonymized_database_subnet_ids" {
  type = list(string)
}

variable "anonymized_database_security_group_ids" {
  type = list(string)
}

variable "anonymized_database_schedule_expression" {
  type = string
}

variable "anonymized_database_instance_type" {
  type = string
}

variable "anonymized_database_subnet_group_name" {
  type = string
}

variable "anonymized_database_kms_key_id" {
  type = string
}

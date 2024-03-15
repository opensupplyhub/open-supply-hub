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

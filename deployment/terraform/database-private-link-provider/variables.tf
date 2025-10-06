# General variables

variable "env_identifier" {
  description = "Environment identifier"
  type        = string
}

variable "project_identifier" {
  description = "Project identifier"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID where the RDS proxy will be created"
  type        = string
}

variable "subnet_ids" {
  description = "List of subnet IDs where the RDS proxy will be created"
  type        = list(string)
}

# Database configuration

variable "db_instance_identifier" {
  description = "Identifier of the RDS instance to connect to the proxy"
  type        = string
}

variable "db_username" {
  description = "Username for the database"
  type        = string
}

variable "db_password" {
  description = "Password for the database"
  type        = string
  sensitive   = true
}

variable "db_port" {
  description = "Port of the database"
  type        = number
}

variable "database_security_group_id" {
  description = "Security group ID of the database"
  type        = string
}

# Connection pool configuration for RDS proxy

variable "connection_borrow_timeout" {
  description = "The number of seconds for a proxy to wait for a connection from the connection pool"
  type        = number
  default     = 120
}

variable "max_connections_percent" {
  description = "The maximum size of the connection pool for each target in a target group"
  type        = number
  default     = 35
}

variable "max_idle_connections_percent" {
  description = "Controls how actively the proxy closes idle database connections in the connection pool"
  type        = number
  default     = 20
}

# Proxy configuration

variable "db_proxy_debug_logging" {
  description = "Whether the proxy includes detailed information about SQL statements in its logs"
  type        = bool
  default     = false
}

variable "idle_client_timeout" {
  description = "The number of seconds that a connection to the proxy can be inactive before the proxy disconnects it"
  type        = number
  default     = 21600
}

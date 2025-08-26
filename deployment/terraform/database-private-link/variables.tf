#------------------------------------------------------------------------------
# RDS Proxy Module Variables
#------------------------------------------------------------------------------

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

variable "db_instance_identifier" {
  description = "Identifier of the RDS instance to connect to the proxy"
  type        = string
}

variable "db_username" {
  description = "Username for the database"
  type        = string
  sensitive   = true
}

variable "db_password" {
  description = "Password for the database"
  type        = string
  sensitive   = true
}

variable "db_port" {
  description = "Port of the database"
  type        = number
  sensitive   = true
}


# Connection pool configuration
variable "connection_borrow_timeout" {
  description = "The number of seconds for a proxy to wait for a connection from the connection pool"
  type        = number
  default     = 120
}

variable "max_connections_percent" {
  description = "The maximum size of the connection pool for each target in a target group"
  type        = number
  default     = 30
}

variable "max_idle_connections_percent" {
  description = "Controls how actively the proxy closes idle database connections in the connection pool"
  type        = number
  default     = 10
}

# Proxy configuration
variable "debug_logging" {
  description = "Whether the proxy includes detailed information about SQL statements in its logs"
  type        = bool
  default     = false
}

variable "idle_client_timeout" {
  description = "The number of seconds that a connection to the proxy can be inactive before the proxy disconnects it"
  type        = number
  default     = 300
}

# Security Configuration
variable "allowed_security_group_id" {
  description = "Security group ID that is allowed to connect to the RDS Proxy"
  type        = string
  default     = ""
}

variable "database_security_group_id" {
  description = "Security group ID of the database"
  type        = string
}

# NLB
# TODO: Rework this to get the IP addresses via Lambda function
variable "db_proxy_ips" {
  description = "List of IP addresses of the database proxy"
  type        = list(string)
}

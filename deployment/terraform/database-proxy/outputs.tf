#------------------------------------------------------------------------------
# RDS Proxy Module Outputs
#------------------------------------------------------------------------------

output "proxy_endpoint" {
  description = "The endpoint of the RDS Proxy"
  value       = aws_db_proxy.main_db.endpoint
}

output "security_group_id" {
  description = "The ID of the security group created for the RDS Proxy"
  value       = aws_security_group.proxy.id
}

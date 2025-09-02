output "vpc_endpoint_dns_name" {
  value = aws_vpc_endpoint.database_vpc_endpoint.dns_entry[0].dns_name
}

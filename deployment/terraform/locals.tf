locals {
  default_tags   = {
    Project = var.project
    Environment = var.environment
  }
  oar_client_key = uuid()
}

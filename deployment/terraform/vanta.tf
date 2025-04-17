module "vanta" {
  count = var.environment == "Test" || var.environment == "Production" ? 1 : 0

  source = "./vanta-iam-role"

  vanta_assumed_role_principals   = var.vanta_assumed_role_principals
  vanta_assumed_role_external_ids = var.vanta_assumed_role_external_ids
}

module "vanta" {
  count = var.environment == "Test" || var.environment == "Production" ? 1 : 0

  source = "./vanta-iam-role"

  vanta_assumed_role_principals   = local.vanta_assumed_role_principals
  vanta_assumed_role_external_ids = local.vanta_assumed_role_external_ids
}

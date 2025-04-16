module "vanta" {
  count = var.environment == "Test" || var.environment == "Production" ? 1 : 0

  source = "./vanta-iam-role"
}

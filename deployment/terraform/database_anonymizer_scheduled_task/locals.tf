locals {
  short        = "${replace(var.project, " ", "")}${var.environment}"
  kms_key_name = join("-", ["shared-snapshot-key", random_id.database_anonymizer.hex])
}

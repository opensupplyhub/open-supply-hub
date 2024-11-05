locals {
  short                          = "${replace(var.project, " ", "")}${var.environment}"
  anonymized_database_dump_image = "${module.ecr_repository_database_anonymizer.repository_url}:${var.anonymized_database_dump_image_tag}"
}

locals {
  env_id_short = "${replace(var.project_identifier, " ", "")}${var.env_identifier}"
}
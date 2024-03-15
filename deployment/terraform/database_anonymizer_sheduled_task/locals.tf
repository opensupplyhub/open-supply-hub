locals {
    short = "${replace(var.project, " ", "")}${var.environment}"
}

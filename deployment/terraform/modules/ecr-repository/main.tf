#
# ECR Resources
#
# Locally vendored copy of github.com/azavea/terraform-aws-ecr-repository (ref 1.0.0),
# extended to expose image_tag_mutability so repositories can enforce immutable tags
# (required by the Vanta "Fargate deploys version-controlled images" control).
# Resource names are kept identical to the upstream module so existing Terraform
# state addresses (module.<name>.aws_ecr_repository.default) are preserved.
#
resource "aws_ecr_repository" "default" {
  name                 = var.repository_name
  image_tag_mutability = var.image_tag_mutability
}

resource "aws_ecr_lifecycle_policy" "default" {
  count = var.attach_lifecycle_policy ? 1 : 0

  repository = aws_ecr_repository.default.name
  policy     = var.lifecycle_policy != "" ? var.lifecycle_policy : file("${path.module}/templates/default-lifecycle-policy.json.tpl")
}

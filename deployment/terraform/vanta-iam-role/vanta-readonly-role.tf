resource "aws_iam_policy" "VantaAdditionalPermissions" {
  name        = "VantaAdditionalPermissions"
  description = "Custom Vanta Policy"
  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Deny",
        "Action" : [
          "datapipeline:EvaluateExpression",
          "datapipeline:QueryObjects",
          "rds:DownloadDBLogFilePortion"
        ],
        "Resource" : "*"
      }
    ]
  })
}

data "aws_iam_policy_document" "assume_role" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]
    principals {
      identifiers = var.vanta_assumed_role_principals
      type        = "AWS"
    }
    condition {
      test     = "StringEquals"
      values   = var.vanta_assumed_role_external_ids
      variable = "sts:ExternalId"
    }
  }
}

resource "aws_iam_role" "vanta-auditor" {
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
  name               = "vanta-auditor"
}

resource "aws_iam_role_policy_attachment" "VantaSecurityAudit" {
  role       = aws_iam_role.vanta-auditor.name
  policy_arn = "arn:aws:iam::aws:policy/SecurityAudit"
}

resource "aws_iam_role_policy_attachment" "VantaAdditionalPermissions" {
  role       = aws_iam_role.vanta-auditor.name
  policy_arn = aws_iam_policy.VantaAdditionalPermissions.arn
}

output "vanta-auditor-arn" {
  description = "The arn from the Terraform created role that you need to input into the Vanta UI at the end of the AWS connection steps."
  value       = aws_iam_role.vanta-auditor.arn
}

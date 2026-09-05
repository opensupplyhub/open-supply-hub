data "aws_canonical_user_id" "current" {
}

#
# S3 resources
#
resource "aws_s3_bucket" "logs" {
  bucket = "${lower(replace(var.project, " ", ""))}-${lower(var.environment)}-logs-${var.aws_region}"
  force_destroy = true
  tags = {
    Name        = "${lower(replace(var.project, " ", ""))}-${lower(var.environment)}-logs-${var.aws_region}"
    Project     = var.project
    Environment = var.environment
  }
}

resource "aws_s3_bucket_acl" "logs" {
  bucket = aws_s3_bucket.logs.id
  acl    = "log-delivery-write"
  depends_on = [aws_s3_bucket_ownership_controls.logs]
  # access_control_policy {

  #   grant {
  #     grantee {
  #       type = "CanonicalUser"
  #       id   = data.aws_canonical_user_id.current.id
  #     }
  #     permission = "FULL_CONTROL"
  #   }

  #   grant {
  #     grantee {
  #       type = "CanonicalUser"
  #       id   = var.aws_cloudfront_canonical_user_id
  #     }
  #     permission = "FULL_CONTROL"
  #   }

  #   owner {
  #     id = data.aws_canonical_user_id.current.id
  #   }

  # }
}

resource "aws_s3_bucket_ownership_controls" "logs" {
  bucket = aws_s3_bucket.logs.id

  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_public_access_block" "logs" {
  bucket = aws_s3_bucket.logs.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket" "files" {
  bucket = local.files_bucket_name
  force_destroy = true
  # acl    = "private"

  tags = {
    Name        = local.files_bucket_name
    Project     = var.project
    Environment = var.environment
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "files" {
  bucket = aws_s3_bucket.files.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "files" {
  bucket = aws_s3_bucket.files.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

data "aws_iam_policy_document" "files" {
  statement {
    sid    = "denyInsecureTransport"
    effect = "Deny"

    actions = [
      "s3:*",
    ]

    resources = [
      aws_s3_bucket.files.arn,
      "${aws_s3_bucket.files.arn}/*",
    ]

    principals {
      type        = "*"
      identifiers = ["*"]
    }

    condition {
      test     = "Bool"
      variable = "aws:SecureTransport"
      values = [
        "false"
      ]
    }
  }

  # OSDEV-3370: reject any presigned request for a claim attachment
  # whose signature is older than 15 minutes, regardless of the expiry
  # the signer asked for. A presigned URL is a bearer token; this caps
  # the damage of a leaked or over-long URL at the policy layer, so no
  # application bug can mint a long-lived one. Direct SDK requests sign
  # per request (signature age ~0s) and are unaffected; claim-attachment
  # downloads use 60-second URLs, well inside this ceiling.
  #
  # Deliberately scoped to the claim_attachments/ prefix, not the whole
  # bucket: facility-list file downloads and PartnerFieldGroup icons
  # (embedded in CloudFront-cached API responses) legitimately rely on
  # longer-lived presigned URLs. Legacy claim attachments at the bucket
  # root are protected by the 60-second URL expiry alone until they are
  # migrated under the prefix (tracked in OSDEV-2278).
  statement {
    sid    = "denyStalePresignedRequests"
    effect = "Deny"

    actions = [
      "s3:*",
    ]

    resources = [
      "${aws_s3_bucket.files.arn}/claim_attachments/*",
    ]

    principals {
      type        = "*"
      identifiers = ["*"]
    }

    condition {
      test     = "NumericGreaterThan"
      variable = "s3:signatureAge"
      values = [
        "900000"
      ]
    }
  }

  # OSDEV-3374: let the automated-claims pipeline (a Lambda in another
  # AWS account) read claim attachments directly via IAM instead of
  # receiving presigned URLs from the API. Read-only, and scoped to the
  # claim_attachments/ prefix — nothing else in the bucket is shared.
  # The role ARNs are provided per environment in uncommitted tfvars;
  # with the default empty list this statement is not emitted at all.
  dynamic "statement" {
    for_each = length(var.claim_attachments_reader_role_arns) > 0 ? [1] : []

    content {
      sid    = "allowClaimAttachmentPipelineRead"
      effect = "Allow"

      actions = [
        "s3:GetObject",
      ]

      resources = [
        "${aws_s3_bucket.files.arn}/claim_attachments/*",
      ]

      principals {
        type        = "AWS"
        identifiers = var.claim_attachments_reader_role_arns
      }
    }
  }
}

resource "aws_s3_bucket_policy" "files" {
  bucket = aws_s3_bucket.files.id
  policy = data.aws_iam_policy_document.files.json
}

#
# ECR resources
#
module "ecr_repository_app" {
  source = "./modules/ecr-repository"

  repository_name = "${lower(replace(var.project, " ", ""))}-${lower(var.environment)}"

  image_tag_mutability    = "IMMUTABLE"
  attach_lifecycle_policy = true
}

module "ecr_repository_app_dd" {
  source = "./modules/ecr-repository"

  repository_name = "${lower(replace(var.project, " ", ""))}-deduplicate-${lower(var.environment)}"

  image_tag_mutability    = "IMMUTABLE"
  attach_lifecycle_policy = true
}


module "ecr_repository_batch" {
  source = "./modules/ecr-repository"

  repository_name = "${lower(replace(var.project, " ", ""))}-batch-${lower(var.environment)}"

  image_tag_mutability    = "IMMUTABLE"
  attach_lifecycle_policy = true
}

module "ecr_repository_kafka" {
  source = "./modules/ecr-repository"

  repository_name = "${lower(replace(var.project, " ", ""))}-kafka-${lower(var.environment)}"

  image_tag_mutability    = "IMMUTABLE"
  attach_lifecycle_policy = true
}

module "ecr_repository_logstash" {
  source = "./modules/ecr-repository"

  repository_name = "${lower(replace(var.project, " ", ""))}-logstash-${lower(var.environment)}"

  image_tag_mutability    = "IMMUTABLE"
  attach_lifecycle_policy = true
}

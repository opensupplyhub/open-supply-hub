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

#
# ECR resources
#
module "ecr_repository_app" {
  source = "github.com/azavea/terraform-aws-ecr-repository?ref=1.0.0"

  repository_name = "${lower(replace(var.project, " ", ""))}-${lower(var.environment)}"

  attach_lifecycle_policy = true
}

module "ecr_repository_app_dd" {
  source = "github.com/azavea/terraform-aws-ecr-repository?ref=1.0.0"

  repository_name = "${lower(replace(var.project, " ", ""))}-deduplicate-${lower(var.environment)}"

  attach_lifecycle_policy = true
}


module "ecr_repository_batch" {
  source = "github.com/azavea/terraform-aws-ecr-repository?ref=1.0.0"

  repository_name = "${lower(replace(var.project, " ", ""))}-batch-${lower(var.environment)}"

  attach_lifecycle_policy = true
}

module "ecr_repository_kafka" {
  source = "github.com/azavea/terraform-aws-ecr-repository?ref=1.0.0"

  repository_name = "${lower(replace(var.project, " ", ""))}-kafka-${lower(var.environment)}"

  attach_lifecycle_policy = true
}

module "ecr_repository_logstash" {
  source = "github.com/azavea/terraform-aws-ecr-repository?ref=1.0.0"

  repository_name = "${lower(replace(var.project, " ", ""))}-logstash-${lower(var.environment)}"

  attach_lifecycle_policy = true
}
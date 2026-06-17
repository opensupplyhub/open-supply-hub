# Dedicated S3 bucket for VPC flow logs, kept separate from the shared logs
# bucket (storage.tf) so flow-log delivery never touches the existing ALB/CDN
# log structure or its bucket policy. S3 delivery needs no IAM role; the
# delivery.logs.amazonaws.com service writes via this bucket's own policy.

resource "aws_s3_bucket" "vpc_flow_logs" {
  bucket        = "${lower(replace(var.project, " ", ""))}-${lower(var.environment)}-vpc-flow-logs-${var.aws_region}"
  force_destroy = false

  tags = {
    Name        = "${lower(replace(var.project, " ", ""))}-${lower(var.environment)}-vpc-flow-logs-${var.aws_region}"
    Project     = var.project
    Environment = var.environment
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "vpc_flow_logs" {
  bucket = aws_s3_bucket.vpc_flow_logs.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_ownership_controls" "vpc_flow_logs" {
  bucket = aws_s3_bucket.vpc_flow_logs.id

  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_public_access_block" "vpc_flow_logs" {
  bucket = aws_s3_bucket.vpc_flow_logs.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Expire flow logs after a year to keep storage costs bounded.
resource "aws_s3_bucket_lifecycle_configuration" "vpc_flow_logs" {
  bucket = aws_s3_bucket.vpc_flow_logs.id

  rule {
    id     = "expire-old-flow-logs"
    status = "Enabled"

    filter {}

    expiration {
      days = 365
    }

    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }
  }
}

data "aws_iam_policy_document" "vpc_flow_logs_s3" {
  statement {
    sid     = "AWSLogDeliveryWrite"
    effect  = "Allow"
    actions = ["s3:PutObject"]

    principals {
      type        = "Service"
      identifiers = ["delivery.logs.amazonaws.com"]
    }

    resources = [
      "${aws_s3_bucket.vpc_flow_logs.arn}/AWSLogs/${data.aws_caller_identity.current.account_id}/*",
    ]

    condition {
      test     = "StringEquals"
      variable = "aws:SourceAccount"
      values   = [data.aws_caller_identity.current.account_id]
    }

    condition {
      test     = "StringEquals"
      variable = "s3:x-amz-acl"
      values   = ["bucket-owner-full-control"]
    }

    condition {
      test     = "ArnLike"
      variable = "aws:SourceArn"
      values   = ["arn:aws:logs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:*"]
    }
  }

  statement {
    sid    = "AWSLogDeliveryAclCheck"
    effect = "Allow"

    actions = [
      "s3:GetBucketAcl",
      "s3:ListBucket",
    ]

    principals {
      type        = "Service"
      identifiers = ["delivery.logs.amazonaws.com"]
    }

    resources = [aws_s3_bucket.vpc_flow_logs.arn]

    condition {
      test     = "StringEquals"
      variable = "aws:SourceAccount"
      values   = [data.aws_caller_identity.current.account_id]
    }

    condition {
      test     = "ArnLike"
      variable = "aws:SourceArn"
      values   = ["arn:aws:logs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:*"]
    }
  }
}

resource "aws_s3_bucket_policy" "vpc_flow_logs" {
  bucket = aws_s3_bucket.vpc_flow_logs.id
  policy = data.aws_iam_policy_document.vpc_flow_logs_s3.json
}

resource "aws_flow_log" "vpc" {
  log_destination_type = "s3"
  log_destination      = aws_s3_bucket.vpc_flow_logs.arn
  traffic_type         = "ALL"
  vpc_id               = module.vpc.id

  destination_options {
    file_format        = "plain-text"
    per_hour_partition = false
  }

  # Ensure the delivery permissions exist before the flow log is created, so
  # log delivery to S3 does not fail on first write. This is a "hidden"
  # dependency Terraform cannot infer, mirroring the ALB access-logging setup.
  depends_on = [aws_s3_bucket_policy.vpc_flow_logs]
}

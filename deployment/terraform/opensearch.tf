resource "aws_security_group" "opensearch" {
  vpc_id = module.vpc.id

  tags = {
    Name        = "sgOpenSearch"
    Project     = var.project
    Environment = var.environment
  }
}

resource "aws_cloudwatch_log_group" "opensearch" {
  name              = "log${local.short}OpenSearch"
  retention_in_days = 30
}

resource "aws_opensearch_domain" "opensearch" {
  domain_name    = "opensearch-domain"
  engine_version = "OpenSearch_2.11"

  access_policies = [
    data.aws_iam_policy_document.opensearch_log_publishing_policy.json,
    data.aws_iam_policy_document.opensearch_access_policy.json
  ]

  cluster_config {
    instance_type          = "t3.small.search"
    instance_count         = 2
    zone_awareness_enabled = true
  }

  ebs_options {
    ebs_enabled = true
    volume_size = 10
  }

  advanced_security_options {
    enabled = true
    master_user_options {
      master_user_arn = aws_iam_role.opensearch_role.arn
    }
  }

  domain_endpoint_options {
    enforce_https       = true
    tls_security_policy = "Policy-Min-TLS-1-2-2019-07"
  }

  encrypt_at_rest {
    enabled = true
  }

  node_to_node_encryption {
    enabled = true
  }

  log_publishing_options {
    cloudwatch_log_group_arn = aws_cloudwatch_log_group.opensearch.arn
    log_type                 = "INDEX_SLOW_LOGS"
  }

  log_publishing_options {
    cloudwatch_log_group_arn = aws_cloudwatch_log_group.opensearch.arn
    log_type                 = "SEARCH_SLOW_LOGS"
  }

  log_publishing_options {
    cloudwatch_log_group_arn = aws_cloudwatch_log_group.opensearch.arn
    log_type                 = "ES_APPLICATION_LOGS"
  }

  log_publishing_options {
    cloudwatch_log_group_arn = aws_cloudwatch_log_group.opensearch.arn
    log_type                 = "AUDIT_LOGS"
  }

  vpc_options {
    subnet_ids         = module.vpc.private_subnet_ids

    security_group_ids = [aws_security_group.opensearch.id]
  }
}

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
  domain_name    = local.opensearch_domain_name
  engine_version = "OpenSearch_2.15"

  cluster_config {
    instance_type          = var.opensearch_instance_type
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
     master_user_arn = aws_iam_role.app_task_role.arn
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

resource "aws_opensearch_domain_policy" "main" {
  domain_name     = aws_opensearch_domain.opensearch.domain_name
  access_policies = data.aws_iam_policy_document.opensearch_access_policy.json
}

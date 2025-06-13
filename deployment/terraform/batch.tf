resource "aws_batch_compute_environment" "default" {
  depends_on = [aws_iam_role_policy_attachment.batch_policy]

  compute_environment_name_prefix = "batch${local.short}DefaultComputeEnvironment"
  type                            = "MANAGED"
  state                           = "ENABLED"
  service_role                    = aws_iam_role.container_instance_batch.arn

  lifecycle {
    create_before_destroy = true
  }

  compute_resources {
    type           = "SPOT"
    bid_percentage = var.batch_default_ce_spot_fleet_bid_percentage
    ec2_key_pair   = var.aws_key_name
    image_id       = var.batch_ami_id

    min_vcpus     = var.batch_default_ce_min_vcpus
    desired_vcpus = var.batch_default_ce_desired_vcpus
    max_vcpus     = var.batch_default_ce_max_vcpus

    spot_iam_fleet_role = aws_iam_role.container_instance_spot_fleet.arn
    instance_role       = aws_iam_instance_profile.container_instance.arn

    instance_type = var.batch_default_ce_instance_types

    security_group_ids = [
      aws_security_group.batch.id,
    ]

    subnets = module.vpc.private_subnet_ids

    tags = {
      Name               = "BatchWorker"
      ComputeEnvironment = "Default"
      Project            = var.project
      Environment        = var.environment
    }
  }
}

resource "aws_batch_job_queue" "default" {
  name                 = "queue${local.short}Default"
  priority             = 1
  state                = "ENABLED"
  compute_environments = [aws_batch_compute_environment.default.arn]
}

data "template_file" "default_job_definition" {
  template = file("job-definitions/default.json")

  vars = {
    image_url                        = "${module.ecr_repository_batch.repository_url}:${var.image_tag}"
    vcpus                            = var.batch_default_job_vcpus
    memory                           = var.batch_default_job_memory
    postgres_host                    = aws_route53_record.database.name
    postgres_port                    = module.database_enc.port
    postgres_user                    = var.rds_database_username
    postgres_password                = var.rds_database_password
    postgres_db                      = var.rds_database_name
    environment                      = var.environment
    django_secret_key                = var.django_secret_key
    google_server_side_api_key       = var.google_server_side_api_key
    oar_client_key                   = var.oar_client_key
    external_domain                  = local.domain_name
    hubspot_api_key                  = var.hubspot_api_key
    hubspot_subscription_id          = var.hubspot_subscription_id
    rollbar_server_side_access_token = var.rollbar_server_side_access_token
    aws_region                       = var.aws_region
    batch_job_queue_name             = "queue${local.short}Default"
    batch_job_def_name               = "job${local.short}Default"
    log_group_name                   = "log${local.short}Batch"
    cache_host                       = aws_route53_record.cache.name
    cache_port                       = var.ec_memcached_port
    aws_storage_bucket_name          = local.files_bucket_name
    data_from_email                  = var.data_from_email
    kafka_bootstrap_servers          = join(",", module.msk_cluster.bootstrap_brokers)
    kafka_topic_basic_name           = var.topic_dedup_basic_name
    opensearch_host                  = aws_opensearch_domain.opensearch.endpoint
    opensearch_port                  = var.opensearch_port
    opensearch_ssl                   = var.opensearch_ssl
    opensearch_ssl_cert_verification = var.opensearch_ssl_cert_verification
  }
}

resource "aws_batch_job_definition" "default" {
  name           = "job${local.short}Default"
  type           = "container"
  propagate_tags = true

  container_properties = data.template_file.default_job_definition.rendered

  retry_strategy {
    attempts = 3
  }
}

resource "aws_batch_compute_environment" "notifications" {
  depends_on = [aws_iam_role_policy_attachment.batch_policy]

  compute_environment_name_prefix = "batch${local.short}NotificationsComputeEnvironment"
  type                            = "MANAGED"
  state                           = "ENABLED"
  service_role                    = aws_iam_role.container_instance_batch.arn

  lifecycle {
    create_before_destroy = true
  }

  compute_resources {
    type                = "SPOT"
    allocation_strategy = "SPOT_CAPACITY_OPTIMIZED"
    bid_percentage      = var.batch_notifications_ce_spot_fleet_bid_percentage
    ec2_key_pair        = var.aws_key_name
    image_id            = var.batch_ami_id

    min_vcpus     = var.batch_notifications_ce_min_vcpus
    desired_vcpus = var.batch_notifications_ce_desired_vcpus
    max_vcpus     = var.batch_notifications_ce_max_vcpus

    spot_iam_fleet_role = aws_iam_role.container_instance_spot_fleet.arn
    instance_role       = aws_iam_instance_profile.container_instance.arn

    instance_type = var.batch_notifications_ce_instance_types

    security_group_ids = [
      aws_security_group.batch.id,
    ]

    subnets = module.vpc.private_subnet_ids

    tags = {
      Name               = "BatchWorker"
      ComputeEnvironment = "Notifications"
      Project            = var.project
      Environment        = var.environment
    }
  }
}

resource "aws_batch_job_queue" "notifications" {
  name                 = "queue${local.short}Notifications"
  priority             = 1
  state                = "ENABLED"
  compute_environments = [aws_batch_compute_environment.notifications.arn]
}

data "template_file" "notifications_job_definition" {
  template = file("job-definitions/notifications.json")

  vars = {
    image_url                        = "${module.ecr_repository_batch.repository_url}:${var.image_tag}"
    postgres_host                    = aws_route53_record.database.name
    postgres_port                    = module.database_enc.port
    postgres_user                    = var.rds_database_username
    postgres_password                = var.rds_database_password
    postgres_db                      = var.rds_database_name
    environment                      = var.environment
    django_secret_key                = var.django_secret_key
    google_server_side_api_key       = var.google_server_side_api_key
    oar_client_key                   = var.oar_client_key
    external_domain                  = local.domain_name
    hubspot_api_key                  = var.hubspot_api_key
    hubspot_subscription_id          = var.hubspot_subscription_id
    rollbar_server_side_access_token = var.rollbar_server_side_access_token
    aws_region                       = var.aws_region
    batch_job_queue_name             = "queue${local.short}Notifications"
    batch_job_def_name               = "job${local.short}Notifications"
    log_group_name                   = "log${local.short}Batch"
    cache_host                       = aws_route53_record.cache.name
    cache_port                       = var.ec_memcached_port
    aws_storage_bucket_name          = local.files_bucket_name
    data_from_email                  = var.data_from_email
    kafka_bootstrap_servers          = join(",", module.msk_cluster.bootstrap_brokers)
    kafka_topic_basic_name           = var.topic_dedup_basic_name
    opensearch_host                  = aws_opensearch_domain.opensearch.endpoint
    opensearch_port                  = var.opensearch_port
    opensearch_ssl                   = var.opensearch_ssl
    opensearch_ssl_cert_verification = var.opensearch_ssl_cert_verification
  }
}

resource "aws_batch_job_definition" "notifications" {
  name           = "job${local.short}Notifications"
  type           = "container"
  propagate_tags = true

  container_properties = data.template_file.notifications_job_definition.rendered

  retry_strategy {
    attempts = 3
  }
}

resource "aws_batch_compute_environment" "export_csv" {
  depends_on = [aws_iam_role_policy_attachment.batch_policy]

  compute_environment_name_prefix = "batch${local.short}ExportCsvComputeEnvironment"
  type                            = "MANAGED"
  state                           = "ENABLED"
  service_role                    = aws_iam_role.container_instance_batch.arn

  lifecycle {
    create_before_destroy = true
  }

  compute_resources {
    type                = "SPOT"
    allocation_strategy = "SPOT_CAPACITY_OPTIMIZED"
    bid_percentage      = var.batch_export_csv_ce_spot_fleet_bid_percentage
    ec2_key_pair        = var.aws_key_name
    image_id            = var.batch_ami_id

    min_vcpus     = var.batch_export_csv_ce_min_vcpus
    desired_vcpus = var.batch_export_csv_ce_desired_vcpus
    max_vcpus     = var.batch_export_csv_ce_max_vcpus

    spot_iam_fleet_role = aws_iam_role.container_instance_spot_fleet.arn
    instance_role       = aws_iam_instance_profile.container_instance.arn

    instance_type = var.batch_export_csv_ce_instance_types

    security_group_ids = [
      aws_security_group.batch.id,
    ]

    subnets = module.vpc.private_subnet_ids

    tags = {
      Name               = "BatchWorker"
      ComputeEnvironment = "ExportCsv"
      Project            = var.project
      Environment        = var.environment
    }
  }
}

resource "aws_batch_job_queue" "export_csv" {
  name                 = "queue${local.short}ExportCsv"
  priority             = 1
  state                = "ENABLED"
  compute_environments = [aws_batch_compute_environment.export_csv.arn]
}

data "template_file" "export_csv_job_definition" {
  template = file("job-definitions/export_csv.json")

  vars = {
    image_url                           = "${module.ecr_repository_batch.repository_url}:${var.image_tag}"
    aws_region                          = var.aws_region
    aws_storage_bucket_name             = local.files_bucket_name
    postgres_host                       = aws_route53_record.database.name
    postgres_port                       = module.database_enc.port
    postgres_user                       = var.rds_database_username
    postgres_password                   = var.rds_database_password
    postgres_db                         = var.rds_database_name
    environment                         = var.environment
    django_secret_key                   = var.django_secret_key
    google_server_side_api_key          = var.google_server_side_api_key
    oar_client_key                      = var.oar_client_key
    external_domain                     = local.domain_name
    batch_job_queue_name                = "queue${local.short}ExportCsv"
    batch_job_def_name                  = "job${local.short}ExportCsv"
    log_group_name                      = "log${local.short}Batch"
    google_service_account_creds_base64 = var.google_service_account_creds_base64
    google_drive_shared_directory_id    = var.google_drive_shared_directory_id
  }
}

resource "aws_batch_job_definition" "export_csv" {
  name           = "job${local.short}ExportCsv"
  type           = "container"
  propagate_tags = true

  container_properties = data.template_file.export_csv_job_definition.rendered

  retry_strategy {
    attempts = 2
  }
}

resource "aws_cloudwatch_event_rule" "export_csv_schedule" {
  name                = "rule${local.short}ExportCsvSchedule"
  description         = "Runs the export_csv job on a schedule"
  schedule_expression = var.export_csv_schedule_expression
  is_enabled          = var.export_csv_enabled
}

resource "aws_cloudwatch_event_target" "export_csv" {
  rule     = aws_cloudwatch_event_rule.export_csv_schedule.name
  arn      = aws_batch_job_queue.export_csv.arn
  role_arn = aws_iam_role.cloudwatch_events_batch_role.arn

  batch_target {
    job_definition = aws_batch_job_definition.export_csv.arn
    job_name       = "job${local.short}ExportCsv"
  }
}

resource "aws_iam_role" "cloudwatch_events_batch_role" {
  name = "evb${local.short}CloudWatchEventsBatchRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "events.amazonaws.com"
        }
      },
    ]
  })
}

data "aws_iam_policy_document" "cloudwatch_events_batch_assume_role" {
  statement {
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["events.amazonaws.com"]
    }
    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role_policy" "cloudwatch_events_batch_role_policy" {
  name   = "evb${local.short}CloudWatchEventsBatchRolePolicy"
  role   = aws_iam_role.cloudwatch_events_batch_role.id
  policy = data.aws_iam_policy_document.cloudwatch_events_batch_policy.json
}

data "aws_iam_policy_document" "cloudwatch_events_batch_policy" {
  statement {
    effect = "Allow"
    actions = [
      "batch:SubmitJob",
      "batch:DescribeJobDefinitions",
      "batch:DescribeJobQueues",
      "batch:DescribeJobs",
    ]
    resources = [
      aws_batch_job_definition.export_csv.arn,
      aws_batch_job_queue.export_csv.arn,
    ]
  }
}

resource "aws_cloudwatch_log_group" "batch" {
  name              = "log${local.short}Batch"
  retention_in_days = 0
}

resource "aws_batch_compute_environment" "direct_data_load" {
  depends_on                      = [aws_iam_role_policy_attachment.batch_policy]
  compute_environment_name_prefix = "batch${local.short}DDLoadComputeEnvironment"
  type                            = "MANAGED"
  state                           = "ENABLED"
  service_role                    = aws_iam_role.container_instance_batch.arn

  lifecycle {
    create_before_destroy = true
  }

  compute_resources {
    type      = "FARGATE"
    max_vcpus = var.batch_direct_data_load_ce_max_vcpus
    subnets   = module.vpc.private_subnet_ids

    security_group_ids = [
      aws_security_group.batch.id,
    ]
  }
}

resource "aws_batch_job_queue" "direct_data_load" {
  name                 = "queue${local.short}DirectDataLoad"
  priority             = 1
  state                = "ENABLED"
  compute_environments = [aws_batch_compute_environment.direct_data_load.arn]
}


data "template_file" "direct_data_load_job_definition" {
  template = file("job-definitions/direct_data_load.json")

  vars = {
    image_url                           = "${module.ecr_repository_batch.repository_url}:${var.image_tag}"
    aws_region                          = var.aws_region
    aws_storage_bucket_name             = local.files_bucket_name
    postgres_host                       = aws_route53_record.database.name
    postgres_port                       = module.database_enc.port
    postgres_user                       = var.rds_database_username
    postgres_password                   = var.rds_database_password
    postgres_db                         = var.rds_database_name
    environment                         = var.environment
    django_secret_key                   = var.django_secret_key
    google_server_side_api_key          = var.google_server_side_api_key
    oar_client_key                      = var.oar_client_key
    external_domain                     = local.domain_name
    batch_job_queue_name                = "queue${local.short}DDLoad"
    batch_job_def_name                  = "job${local.short}DDLoad"
    log_group_name                      = "log${local.short}Batch"
    google_service_account_creds_base64 = var.google_service_account_creds_base64
    google_drive_shared_directory_id    = var.google_drive_shared_directory_id
    sheet_id                            = var.direct_data_load_sheet_id
    contributor_name                    = var.direct_data_load_contributor_name
    contributor_email                   = var.direct_data_load_contributor_email
    user_id                             = var.direct_data_load_user_id
    sheet_name                          = var.direct_data_load_sheet_name
    tab_id                              = var.direct_data_load_tab_id
    opensearch_host                     = aws_opensearch_domain.opensearch.endpoint
    opensearch_port                     = var.opensearch_port
    opensearch_ssl                      = var.opensearch_ssl
    opensearch_ssl_cert_verification    = var.opensearch_ssl_cert_verification
  }
}

resource "aws_batch_job_definition" "direct_data_load" {
  name           = "job${local.short}DirectDataLoad"
  type           = "container"
  propagate_tags = true

  platform_capabilities = ["EC2"]

  container_properties = data.template_file.direct_data_load_job_definition.rendered

  retry_strategy {
    attempts = 2
  }
}

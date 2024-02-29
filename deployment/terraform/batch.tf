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
    kafka_bootstrap_servers                = join (",", module.msk_cluster.bootstrap_brokers)
    kafka_topic_basic_name           = var.topic_dedup_basic_name
  }
}

resource "aws_batch_job_definition" "default" {
  name = "job${local.short}Default"
  type = "container"

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
    kafka_bootstrap_servers                = join (",", module.msk_cluster.bootstrap_brokers)
    kafka_topic_basic_name           = var.topic_dedup_basic_name
  }
}

resource "aws_batch_job_definition" "notifications" {
  name = "job${local.short}Notifications"
  type = "container"

  container_properties = data.template_file.notifications_job_definition.rendered

  retry_strategy {
    attempts = 3
  }
}

#
# CloudWatch Resources
#
resource "aws_cloudwatch_log_group" "batch" {
  name              = "log${local.short}Batch"
  retention_in_days = 0
}

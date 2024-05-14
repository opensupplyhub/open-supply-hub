locals {
  short             = "${replace(var.project, " ", "")}${var.environment}"
  files_bucket_name = lower("${replace(var.project, " ", "")}-${var.environment}-files-${var.aws_region}")
}

variable "project" {
  default = "Open Supply Hub"
}

variable "short_project" {
  default = "osh"
}

variable "environment" {
  default = "Staging"
}

variable "aws_region" {
  default = "eu-west-1"
}

variable "aws_availability_zones" {
  default = ["eu-west-1a", "eu-west-1b"]
}

variable "aws_key_name" {
}

variable "r53_service_discovery_zone" {
  default = "ogr-service.internal"
}

variable "r53_private_hosted_zone" {
}

variable "r53_public_hosted_zone" {
}

variable "cloudfront_price_class" {
}

variable "cloudfront_auth_token" {
}

variable "vpc_cidr_block" {
  default = "10.0.0.0/16"
}

variable "external_access_cidr_blocks" {
  sensitive = true
}

variable "vpc_private_subnet_cidr_blocks" {
  default = ["10.0.1.0/24", "10.0.3.0/24"]
}

variable "vpc_public_subnet_cidr_blocks" {
  default = ["10.0.0.0/24", "10.0.2.0/24"]
}

variable "bastion_ami" {
}

variable "bastion_instance_type" {
}

variable "rds_allocated_storage" {
  default = "64"
}

variable "rds_engine_version" {
  default = "12.4"
}

variable "rds_parameter_group_family" {
  default = "postgres12"
}

variable "rds_instance_type" {
  default = "db.t3.micro"
}

variable "rds_storage_type" {
  default = "gp2"
}

variable "rds_database_identifier" {
}

variable "rds_database_name" {
}

variable "rds_database_username" {
}

variable "rds_database_password" {
  sensitive = true
}

variable "rds_backup_retention_period" {
  default = "30"
}

variable "rds_backup_window" {
  default = "04:00-04:30"
}

variable "rds_maintenance_window" {
  default = "sun:04:30-sun:05:30"
}

variable "rds_auto_minor_version_upgrade" {
  default = true
}

variable "rds_final_snapshot_identifier" {
  default = "osh-rds-snapshot"
}

variable "rds_monitoring_interval" {
  default = "60"
}

variable "rds_skip_final_snapshot" {
  default = false
}

variable "rds_copy_tags_to_snapshot" {
  default = true
}

variable "rds_multi_az" {
  default = false
}

variable "rds_storage_encrypted" {
  sensitive = true
  default   = false
}

variable "rds_seq_page_cost" {
  default = "1"
}

variable "rds_random_page_cost" {
  default = "1"
}

variable "rds_log_min_duration_statement" {
  default = "500"
}

variable "rds_log_connections" {
  default = "0"
}

variable "rds_log_disconnections" {
  default = "0"
}

variable "rds_log_lock_waits" {
  default = "1"
}

variable "rds_log_temp_files" {
  default = "500"
}

variable "rds_log_autovacuum_min_duration" {
  default = "250"
}

variable "rds_cpu_threshold_percent" {
  default = "75"
}

variable "rds_disk_queue_threshold" {
  default = "10"
}

variable "rds_free_disk_threshold_bytes" {
  default = "5000000000"
}

variable "rds_free_memory_threshold_bytes" {
  default = "128000000"
}

variable "rds_cpu_credit_balance_threshold" {
  default = "30"
}

variable "rds_work_mem" {
  default = "20000"
}

variable "rds_deletion_protection" {
  default = true
}

variable "app_ecs_desired_count" {
  default = "1"
}

variable "app_ecs_deployment_min_percent" {
  default = "100"
}

variable "app_ecs_deployment_max_percent" {
  default = "200"
}

variable "app_ecs_grace_period_seconds" {
  default = "180"
}

variable "app_cc_ecs_desired_count" {
  default = "0"
}

variable "app_cc_ecs_deployment_min_percent" {
  default = "100"
}

variable "app_cc_ecs_deployment_max_percent" {
  default = "200"
}

variable "app_cc_ecs_grace_period_seconds" {
  default = "180"
}

variable "app_fargate_cpu" {
  default = "256"
}

variable "app_fargate_memory" {
  default = "512"
}

variable "app_cc_fargate_cpu" {
  default = "512"
}

variable "app_cc_fargate_memory" {
  default = "1024"
}

variable "app_dd_fargate_cpu" {
  default = "512"
}

variable "app_dd_fargate_memory" {
  default = "1024"
}

variable "app_logstash_fargate_cpu" {
  type    = number
  default = 512
}

variable "app_logstash_fargate_memory" {
  type    = number
  default = 3072
}

variable "cli_fargate_cpu" {
  default = "256"
}

variable "cli_fargate_memory" {
  default = "1024"
}

variable "image_tag" {
}

variable "app_port" {
  default = "8080"
}

variable "app_cc_port" {
  default = "80"
}

variable "gunicorn_worker_timeout" {
  default = "180"
}

variable "google_server_side_api_key" {
  sensitive = true
}

variable "google_client_side_api_key" {
  sensitive = true
}

variable "google_analytics_key" {
  default   = ""
  sensitive = true
}

variable "rollbar_server_side_access_token" {
  sensitive = true
}

variable "rollbar_client_side_access_token" {
  sensitive = true
}

variable "django_secret_key" {
  sensitive = true
}

variable "default_from_email" {
}

variable "data_from_email" {
}

variable "notification_email_to" {
}

variable "hubspot_api_key" {
  default   = ""
  sensitive = true
}

variable "hubspot_subscription_id" {
  default = ""
}

variable "batch_default_ce_spot_fleet_bid_percentage" {
  default = "40"
}

variable "batch_notifications_ce_spot_fleet_bid_percentage" {
  default = "40"
}

variable "batch_ami_id" {
  # Latest ECS-optimized Amazon Linux AMI in eu-west-1
  # See: https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-optimized_AMI.html
  default = "ami-002e2fef4b94f8fd0"
}

variable "batch_default_job_vcpus" {
  default = 2
}

variable "batch_default_job_memory" {
  default = 4096
}

variable "batch_default_ce_min_vcpus" {
  default = "0"
}

variable "batch_default_ce_desired_vcpus" {
  default = "0"
}

variable "batch_default_ce_max_vcpus" {
  default = "16"
}

variable "batch_default_ce_instance_types" {
  type = list(string)

  default = [
    "c5",
    "m5",
  ]
}

variable "batch_notifications_ce_min_vcpus" {
  default = "0"
}

variable "batch_notifications_ce_desired_vcpus" {
  default = "0"
}

variable "batch_notifications_ce_max_vcpus" {
  default = "16"
}

variable "batch_notifications_ce_instance_types" {
  type = list(string)

  default = [
    "c5",
    "m5",
  ]
}

variable "app_cli_state_machine_timeout_seconds" {
  default = "600"
}

variable "check_api_limits_schedule_expression" {
  default = "rate(1 hour)"
}

variable "ec2_service_role_policy_arn" {
  default = "arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceforEC2Role"
}

variable "batch_service_role_policy_arn" {
  default = "arn:aws:iam::aws:policy/service-role/AWSBatchServiceRole"
}

variable "spot_fleet_service_role_policy_arn" {
  default = "arn:aws:iam::aws:policy/service-role/AmazonEC2SpotFleetTaggingRole"
}

variable "aws_lambda_service_role_policy_arn" {
  default = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

variable "oar_client_key" {
  sensitive = true
}

variable "aws_cloudfront_canonical_user_id" {
  default = "c4c1ede66af53448b93c283ce9448c4ba468c9432aa01d700d3878632f77d2d0"
}

variable "ec_memcached_identifier" {}

variable "ec_memcached_port" {
  default = 11211
}

variable "ec_memcached_parameter_group_family" {
  default = "memcached1.6"
}

variable "ec_memcached_maintenance_window" {
  default = "sun:02:30-sun:03:30"
}

variable "ec_memcached_desired_clusters" {
  default = 1
}

variable "ec_memcached_instance_type" {
  default = "cache.t3.medium"
}

variable "ec_memcached_engine_version" {
  default = "1.6.12"
}

variable "ec_memcached_alarm_cpu_threshold_percent" {
  default = "75"
}

variable "ec_memcached_alarm_memory_threshold_bytes" {
  default = "10000000"
}

variable "ec_memcached_max_item_size" {
  # 1MB
  default = "1048576"
}

variable "py_environment" {
  default = "Staging"
}
variable "CORS_ALLOWED_ORIGIN_REGEXES" {
  type = string
  default = "http://localhost, https://127.0.0.1"
}

variable "topic_dedup_basic_name" {
  default = "basic_name"
}

variable "consumer_client_id" {
  default = "user"
}

variable "consumer_group_id" {
  default = "group"
}

variable "app_dd_ecs_desired_count" {
  default = "1"
}

variable "app_dd_ecs_deployment_min_percent" {
  default = "100"
}

variable "app_dd_ecs_deployment_max_percent" {
  default = "200"
}

variable "security_protocol" {
  default = "SSL"
}

variable "claim_from_email" {
  default = "claims@opensupplyhub.org"
}

variable "dedupe_hub_live" {
  default = false
}

variable "dedupe_hub_name" {
}
variable "dedupe_hub_version" {
}

variable "app_logstash_ecs_desired_count" {
  type    = number
  default = 0 # Temporary set to zero to prevent money consumption.
}

variable "app_logstash_ecs_deployment_min_percent" {
  type    = number
  default = 100
}

variable "app_logstash_ecs_deployment_max_percent" {
  type    = number
  default = 200
}

variable "anonymizer_destination_aws_account" {
  type    = string
  default = ""
}

variable "anonymizer_db_identifier" {
  type    = string
  default = "database-anonymizer"
}

variable "anonymizer_image_tag" {
  type    = string
  default = "v0.0.1"
}

variable "anonymizer_schedule_expression" {
  type    = string
  default = "cron(0 10 ? * SAT *)"
}

variable "anonymizer_kms_key_admin_users" {
  type    = list
  default = []
}

variable "database_anonymizer_enabled" {
  type    = bool
  default = false
}

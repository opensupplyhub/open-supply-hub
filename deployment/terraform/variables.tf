locals {
  short                  = "${replace(var.project, " ", "")}${var.environment}"
  files_bucket_name      = lower("${replace(var.project, " ", "")}-${var.environment}-files-${var.aws_region}")
  opensearch_domain_name = "${lower("${var.environment}")}-os-domain"
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
  default = "16"
}

variable "rds_parameter_group_family" {
  default = "postgres16"
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

variable "rds_allow_major_version_upgrade" {
  default     = false
  type        = bool
  description = "Indicates that major PostgreSQL engine version upgrades are allowed."
}

variable "rds_apply_immediately" {
  default     = false
  type        = bool
  description = "Specifies whether any database modifications are applied immediately, or during the next maintenance window."
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

variable "snapshot_identifier" {
  default     = ""
  type        = string
  description = "The name of the snapshot (if any) the database should be created from"
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
  default = 2048
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

variable "opensearch_port" {
  default = "443"
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

variable "batch_export_csv_ce_spot_fleet_bid_percentage" {
  type    = number
  default = 60
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

variable "batch_export_csv_ce_min_vcpus" {
  type    = number
  default = 0
}

variable "batch_notifications_ce_desired_vcpus" {
  default = "0"
}

variable "batch_export_csv_ce_desired_vcpus" {
  type    = number
  default = 0
}

variable "batch_notifications_ce_max_vcpus" {
  default = "16"
}

variable "batch_export_csv_ce_max_vcpus" {
  type    = number
  default = 4
}

variable "batch_notifications_ce_instance_types" {
  type = list(string)

  default = [
    "c5",
    "m5",
  ]
}

variable "batch_export_csv_ce_instance_types" {
  type = list(string)

  default = [
    "c5",
    "m5",
    "m4",
    "c4",
  ]
}

variable "app_cli_state_machine_timeout_seconds" {
  default = "600"
}

variable "check_api_limits_schedule_expression" {
  default = "rate(1 hour)"
}

variable "update_expired_download_limits_schedule_expression" {
  default = "cron(0 0 * * ? *)" # Once per day at 00:00 UTC.
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

variable "CORS_ALLOWED_ORIGIN_REGEXES" {
  type    = string
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
variable "instance_source" {
  default = "os_hub"
}

variable "opensearch_instance_type" {
  type    = string
  default = "t3.small.search"
}

variable "opensearch_auth_type" {
  type    = string
  default = "aws_iam"
}

variable "opensearch_ssl" {
  type    = bool
  default = true
}

variable "opensearch_ssl_cert_verification" {
  type    = bool
  default = true
}

variable "production_locations_pipeline_update_interval_minutes" {
  type    = number
  default = 15
}

variable "moderation_events_pipeline_update_interval_minutes" {
  type    = number
  default = 1
}

variable "app_logstash_ecs_desired_count" {
  type    = number
  default = 1
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
  type    = list(any)
  default = []
}

variable "database_anonymizer_enabled" {
  type    = bool
  default = false
}

variable "anonymized_database_dump_enabled" {
  type    = bool
  default = false
}

variable "anonymized_database_kms_key_id" {
  type    = string
  default = ""
}

variable "anonymized_database_instance_type" {
  type    = string
  default = "db.t3.micro"
}

variable "anonymized_database_identifier" {
  type    = string
  default = "database-anonymizer"
}

variable "anonymized_database_schedule_expression" {
  type    = string
  default = "cron(0 5 ? * SAT *)"
}

variable "anonymized_database_name" {
  type    = string
  default = ""
}

variable "anonymized_database_username" {
  type    = string
  default = ""
}

variable "anonymized_database_password" {
  type      = string
  default   = ""
  sensitive = true
}

variable "export_csv_enabled" {
  description = "Toggle to enable or disable the export csv scheduled job"
  type        = bool
  default     = true
}

variable "export_csv_schedule_expression" {
  type        = string
  default     = "cron(0 0 1 * ? *)"
  description = "The schedule expression for the export csv job"
}

variable "google_service_account_creds_base64" {
  type        = string
  sensitive   = true
  description = "Base64-encoded Google service account key"
}

variable "google_drive_shared_directory_id" {
  type        = string
  sensitive   = true
  description = "The ID of the shared directory in Google Drive"
}

variable "app_ecs_max_cpu_threshold" {
  description = "Threshold for max CPU usage"
  default     = 85
  type        = number
}

variable "app_ecs_min_cpu_threshold" {
  description = "Threshold for min CPU usage"
  default     = 10
  type        = number
}

variable "app_ecs_max_cpu_evaluation_period" {
  description = "The number of periods over which data is compared to the specified threshold for max cpu metric alarm"
  default     = 3
  type        = number
}

variable "app_ecs_min_cpu_evaluation_period" {
  description = "The number of periods over which data is compared to the specified threshold for min cpu metric alarm"
  default     = 3
  type        = number
}

variable "app_ecs_max_cpu_period" {
  description = "The period in seconds over which the specified statistic is applied for max cpu metric alarm"
  default     = 60
  type        = number
}

variable "app_ecs_min_cpu_period" {
  description = "The period in seconds over which the specified statistic is applied for min cpu metric alarm"
  default     = 60
  type        = number
}

variable "app_ecs_scale_target_max_capacity" {
  description = "The max capacity of the scalable target"
  default     = 5
  type        = number
}

variable "app_ecs_scale_target_min_capacity" {
  description = "The min capacity of the scalable target"
  default     = 1
  type        = number
}

variable "app_ecs_cooldown_scale_up" {
  description = "Cooldown period for scaling actions"
  default     = 60
  type        = number
}

variable "app_ecs_cooldown_scale_down" {
  description = "Cooldown period for scaling actions"
  default     = 60
  type        = number
}

variable "vanta_assumed_role_external_ids" {
  type      = list(any)
  default   = []
  sensitive = true
}

variable "vanta_assumed_role_principals" {
  type      = list(any)
  default   = []
  sensitive = true
}

variable "ip_whitelist" {
  type        = list(string)
  default     = []
  description = "List of IP addresses to allow through the AWS WAF"
}

variable "ip_denylist" {
  type        = list(string)
  default     = []
  description = "List of IP addresses to block through the AWS WAF"
}

variable "waf_enabled" {
  type    = bool
  default = false
}


### DIRECT DATA LOAD VARIABLES - START ###

variable "direct_data_load_sheet_id" {
  type        = string
  description = "Google Sheet ID for direct data load"
}

variable "direct_data_load_contributor_name" {
  type        = string
  description = "Contributor name for direct data load"
}

variable "direct_data_load_contributor_email" {
  type        = string
  description = "Contributor email for direct data load"
}

variable "direct_data_load_user_id" {
  type        = number
  description = "User ID for direct data load"
}

variable "direct_data_load_sheet_name" {
  type        = string
  description = "Name of the Google Sheet for direct data load"
}

variable "direct_data_load_tab_id" {
  type        = number
  description = "Tab ID of the Google Sheet for direct data load"
}

### DIRECT DATA LOAD VARIABLES - END ###

variable "stripe_secret_key" {
  type        = string
  sensitive   = true
  description = "Stripe secret key for payment processing"
}

variable "stripe_webhook_secret" {
  type        = string
  sensitive   = true
  description = "Stripe webhook secret for payment processing"
}

variable "stripe_price_id" {
  type        = string
  description = "Stripe price ID for subscription plans"
}

variable "dark_visitors_project_key" {
  type        = string
  description = "Dark Visitors project key"
}

variable "dark_visitors_token" {
  type        = string
  description = "Dark Visitors token"
  sensitive   = true
}

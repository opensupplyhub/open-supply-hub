project = "OpenSupplyHub"
environment = "Test"

aws_region = "eu-west-1"
aws_availability_zones = ["eu-west-1a", "eu-west-1b"]

r53_private_hosted_zone = "osh.internal"
r53_service_discovery_zone = "sd.internal"
r53_public_hosted_zone = "os-hub.net"

cloudfront_price_class = "PriceClass_All"

api_facilities_cache_default_ttl           = 60
api_facilities_cache_max_ttl               = 60
api_production_locations_cache_default_ttl = 60
api_production_locations_cache_max_ttl     = 60

bastion_ami = "ami-03a25ed280b358f5b"
bastion_instance_type = "t3.nano"

rds_allocated_storage = "400"
rds_engine_version = "16"
rds_parameter_group_family = "postgres16"
rds_instance_type = "db.t3.2xlarge"
rds_database_identifier = "opensupplyhub-enc-tst"
rds_database_name = "opensupplyhub"
rds_multi_az = false
rds_storage_type = "gp3"
rds_iops = 12000
rds_storage_encrypted = true
# ~80% of max_connections for db.t3.2xlarge (3604)
rds_database_connections_alarm_threshold = "2880"
# ~5% of 32 GiB RAM; ~10% of 400 GB storage
rds_free_memory_threshold_bytes = "1600000000"
rds_free_disk_threshold_bytes   = "40000000000"

anonymized_database_instance_type = "db.t3.2xlarge"
anonymized_database_identifier = "database-anonymizer"
anonymized_database_schedule_expression = "cron(0 5 ? * SAT *)"
anonymized_database_dump_enabled = true

# Ephemeral GitHub Actions runner on CodeBuild for DB dump/restore jobs.
# The CodeConnections connection ARN is stored in Secrets Manager
# (codebuild_github_runner_connection_secret_name) after one-time OAuth setup.
codebuild_github_runner_enabled = true

app_ecs_desired_count = "2"
app_ecs_deployment_min_percent = "100"
app_ecs_deployment_max_percent = "400"
app_fargate_cpu = "2048"
app_fargate_memory = "4096"

app_ecs_max_cpu_threshold         = 85
app_ecs_min_cpu_threshold         = 15
app_ecs_scale_target_max_capacity = 2
app_ecs_scale_target_min_capacity = 1
app_ecs_cooldown_scale_down       = 300
app_ecs_cooldown_scale_up         = 180

app_dd_fargate_cpu = "8192"
app_dd_fargate_memory = "40960"
app_dd_ecs_desired_count = "1"

cli_fargate_cpu = "2048"
cli_fargate_memory = "8192"

gunicorn_worker_timeout = "240"
gunicorn_workers        = "5"

batch_default_ce_spot_fleet_bid_percentage = 60
batch_ami_id = "ami-002e2fef4b94f8fd0"

batch_default_ce_min_vcpus = 0
batch_default_ce_max_vcpus = 128
batch_default_job_memory = 8192

batch_default_ce_instance_types = ["c5", "m5"]

app_ecs_grace_period_seconds = 300

ec_memcached_identifier = "opensupplyhub-tst"
rds_final_snapshot_identifier = "opensupplyhub-rds-tst"
topic_dedup_basic_name = "basic-name"
dedupe_hub_live = true
dedupe_hub_name = "deduplicate"
dedupe_hub_version = 1

opensearch_instance_type = "t3.small.search"

app_logstash_fargate_cpu = 256
app_logstash_fargate_memory = 2048

instance_source= "os_hub"

vpn_ec2_ami = "ami-0940c95b23a1f7cac"

enable_homepage_proxy   = true
craft_cms_origin_domain = "open-supply.staging.servd.dev"

# Owns the shared-account Chatbot Slack channel config (Dev/Test/Preprod).
# Sibling SNS ARNs live in SM (aws_chatbot_additional_sns_topic_arns_secret_name).
# Dev/Preprod set aws_chatbot_manage_channel_configuration = false.
aws_chatbot_manage_channel_configuration = true

# ---------------------------------------------------------------------------
# Config transferred from private ci-deployment (plain values)
# ---------------------------------------------------------------------------
waf_enabled = true
memcached_view_cache_timeout_seconds = 360
stripe_price_id = "price_1RdvmXPN2tV5nf0j18Vaed5v"
hubspot_subscription_id = "12847627"
dromo_schema_id = "6f3e129c-d724-4b80-b2c9-8e54b47e8017"
google_drive_shared_directory_id = "18ld9-YuqJZZE1GwBx47nih1lUJDM-3m4"
aws_chatbot_slack_team_id = "T24EH70RW"
aws_chatbot_slack_channel_id = "C07FT2TLE72"
aws_key_name = "osh-tst"

# ---------------------------------------------------------------------------
# AWS Secrets Manager secret names
# Values live in SM; Terraform/CI resolve by name (no account IDs/ARNs in git).
# ---------------------------------------------------------------------------
rds_master_secret_name = "oshub/test/rds-master"
django_secret_key_secret_name = "oshub/test/django-secret-key"
cloudfront_auth_token_secret_name = "oshub/test/cloudfront-auth-token"
default_from_email_secret_name = "oshub/test/default-from-email"
data_from_email_secret_name = "oshub/test/data-from-email"
notification_email_to_secret_name = "oshub/test/notification-email-to"
claim_from_email_secret_name = "oshub/test/claim-from-email"
google_server_side_api_key_secret_name = "oshub/test/google-server-side-api-key"
google_client_side_api_key_secret_name = "oshub/test/google-client-side-api-key"
google_analytics_key_secret_name = "oshub/test/google-analytics-key"
google_service_account_creds_base64_secret_name = "oshub/test/google-service-account-creds-base64"
rollbar_server_side_access_token_secret_name = "oshub/test/rollbar-server-side-access-token"
rollbar_client_side_access_token_secret_name = "oshub/test/rollbar-client-side-access-token"
oar_client_key_secret_name = "oshub/test/oar-client-key"
hubspot_api_key_secret_name = "oshub/test/hubspot-api-key"
stripe_secret_key_secret_name = "oshub/test/stripe-secret-key"
stripe_webhook_secret_secret_name = "oshub/test/stripe-webhook-secret"
dark_visitors_token_secret_name = "oshub/test/dark-visitors-token"
dark_visitors_project_key_secret_name = "oshub/test/dark-visitors-project-key"
dromo_license_key_secret_name = "oshub/test/dromo-license-key"
external_access_cidr_blocks_secret_name = "oshub/test/external-access-cidr-blocks"
ip_denylist_secret_name = "oshub/test/ip-denylist"
anonymized_database_name_secret_name = "oshub/test/anonymized-database-name"
anonymized_database_username_secret_name = "oshub/test/anonymized-database-username"
anonymized_database_password_secret_name = "oshub/test/anonymized-database-password"
anonymized_database_kms_key_id_secret_name = "oshub/test/anonymized-database-kms-key-id"
codebuild_github_runner_connection_secret_name = "oshub/test/codebuild-github-runner-connection"
aws_chatbot_additional_sns_topic_arns_secret_name = "oshub/test/aws-chatbot-additional-sns-topic-arns"
vanta_assumed_role_external_ids_secret_name = "oshub/test/vanta-assumed-role-external-ids"
vanta_assumed_role_principals_secret_name = "oshub/test/vanta-assumed-role-principals"
contribot_os_hub_api_token_secret_name = "oshub/test/contribot-os-hub-api-token"
contribot_monday_api_key_secret_name = "oshub/test/contribot-monday-api-key"
contribot_slack_api_url_secret_name = "oshub/test/contribot-slack-api-url"
contribot_google_drive_service_key_secret_name = "oshub/test/contribot-google-drive-service-key"

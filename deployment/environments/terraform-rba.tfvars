project     = "OpenSupplyHub"
environment = "Rba"

aws_region             = "eu-west-1"
aws_availability_zones = ["eu-west-1a", "eu-west-1b"]

r53_private_hosted_zone = "osh.internal"
r53_public_hosted_zone  = "opensupplyhub.org"

cloudfront_price_class = "PriceClass_All"

api_facilities_cache_default_ttl           = 120
api_facilities_cache_max_ttl               = 120
api_production_locations_cache_default_ttl = 120
api_production_locations_cache_max_ttl     = 120

bastion_ami           = "ami-03a25ed280b358f5b"
bastion_instance_type = "t3.nano"

rds_allocated_storage      = "256"
rds_engine_version         = "16"
rds_parameter_group_family = "postgres16"
rds_instance_type          = "db.m6in.4xlarge"
rds_database_identifier    = "opensupplyhub-enc-rba"
rds_database_name          = "opensupplyhub"
rds_multi_az               = false
rds_storage_encrypted      = true
# ~80% of capped max_connections for db.m6in.4xlarge (5000)
rds_database_connections_alarm_threshold = "4000"
# ~5% of 64 GiB RAM; ~10% of 256 GB storage
rds_free_memory_threshold_bytes = "3200000000"
rds_free_disk_threshold_bytes   = "25000000000"

app_ecs_desired_count          = "4"
app_ecs_deployment_min_percent = "100"
app_ecs_deployment_max_percent = "400"
app_ecs_grace_period_seconds   = "420"
app_fargate_cpu                = "1024"
app_fargate_memory             = "2048"

app_ecs_max_cpu_threshold         = 85
app_ecs_min_cpu_threshold         = 15
app_ecs_scale_target_max_capacity = 4
app_ecs_scale_target_min_capacity = 2
app_ecs_cooldown_scale_down       = 300
app_ecs_cooldown_scale_up         = 180

cli_fargate_cpu    = "1024"
cli_fargate_memory = "8192"

batch_default_ce_spot_fleet_bid_percentage = 60
batch_ami_id                               = "ami-002e2fef4b94f8fd0"

batch_default_ce_min_vcpus = 0
batch_default_ce_max_vcpus = 128
batch_default_job_memory   = 8192

batch_default_ce_instance_types = ["c5", "m5"]

gunicorn_worker_timeout = "360"
gunicorn_workers        = "3"

ec_memcached_identifier = "opensupplyhub-rba"

rds_final_snapshot_identifier = "opensupplyhub-rds-rba"
topic_dedup_basic_name        = "basic-name"
dedupe_hub_live               = true
dedupe_hub_name               = "deduplicate"
dedupe_hub_version            = 1
app_dd_fargate_cpu            = 8192
app_dd_fargate_memory         = 40960
app_dd_ecs_desired_count      = 1
django_log_level              = "DEBUG"

opensearch_instance_type = "m6g.large.search"

app_logstash_fargate_cpu    = 256
app_logstash_fargate_memory = 2048

export_csv_enabled = false

db_sync_max_retries     = 3
db_sync_chunk_size = 50000

instance_source = "rba"

vpn_ec2_ami = "ami-0940c95b23a1f7cac"

db_sync_enabled                   = true
db_sync_schedule_expression       = "cron(0 7 * * ? *)" # (7:00 AM UTC)
is_database_private_link_consumer = true

enable_homepage_proxy   = false
craft_cms_origin_domain = ""

# Shares Chatbot channel config with Production (same Slack channel / shared account).
aws_chatbot_manage_channel_configuration = false

waf_enabled = true
memcached_view_cache_timeout_seconds = 360
stripe_price_id = ""
dromo_schema_id = ""
google_drive_shared_directory_id = ""
aws_key_name = "osh-rba"

rds_master_secret_name = "oshub/rba/rds-master"
django_secret_key_secret_name = "oshub/rba/django-secret-key"
cloudfront_auth_token_secret_name = "oshub/rba/cloudfront-auth-token"
default_from_email_secret_name = "oshub/rba/default-from-email"
data_from_email_secret_name = "oshub/rba/data-from-email"
notification_email_to_secret_name = "oshub/rba/notification-email-to"
claim_from_email_secret_name = "oshub/rba/claim-from-email"
google_server_side_api_key_secret_name = "oshub/rba/google-server-side-api-key"
google_client_side_api_key_secret_name = "oshub/rba/google-client-side-api-key"
google_service_account_creds_base64_secret_name = "oshub/rba/google-service-account-creds-base64"
oar_client_key_secret_name = "oshub/rba/oar-client-key"
external_access_cidr_blocks_secret_name = "oshub/rba/external-access-cidr-blocks"
ip_whitelist_secret_name = "oshub/rba/ip-whitelist"
source_db_name_secret_name = "oshub/rba/source-db-name"
source_db_user_secret_name = "oshub/rba/source-db-user"
source_db_password_secret_name = "oshub/rba/source-db-password"
source_db_port_secret_name = "oshub/rba/source-db-port"
database_private_link_vpc_endpoint_service_name_secret_name = "oshub/rba/database-private-link-vpc-endpoint-service-name"
email_anonymization_secret_secret_name = "oshub/rba/email-anonymization-secret"
contribot_os_hub_api_token_secret_name = "oshub/rba/contribot-os-hub-api-token"
contribot_monday_api_key_secret_name = "oshub/rba/contribot-monday-api-key"
contribot_slack_api_url_secret_name = "oshub/rba/contribot-slack-api-url"
contribot_google_drive_service_key_secret_name = "oshub/rba/contribot-google-drive-service-key"

project     = "OpenSupplyHub"
environment = "Production"

aws_region             = "eu-west-1"
aws_availability_zones = ["eu-west-1a", "eu-west-1b"]

r53_private_hosted_zone = "osh.internal"
r53_public_hosted_zone  = "opensupplyhub.org"

# Owns query logging for opensupplyhub.org, which Rba also points at, and for
# openapparel.org, which no environment points at.
route53_query_logging_enabled = true
route53_query_log_extra_zones = ["openapparel.org"]

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
rds_database_identifier    = "opensupplyhub-enc-prd"
rds_database_name          = "opensupplyhub"
rds_multi_az               = false
rds_storage_encrypted      = true
# ~80% of capped max_connections for db.m6in.4xlarge (5000)
rds_database_connections_alarm_threshold = "4000"
# ~5% of 64 GiB RAM; ~10% of 256 GB storage
rds_free_memory_threshold_bytes = "3200000000"
rds_free_disk_threshold_bytes   = "25000000000"

app_ecs_desired_count          = "10"
app_ecs_deployment_min_percent = "100"
app_ecs_deployment_max_percent = "400"
app_ecs_grace_period_seconds   = "420"
app_fargate_cpu                = "2048"
app_fargate_memory             = "4096"

app_ecs_max_cpu_threshold         = 85
app_ecs_min_cpu_threshold         = 15
app_ecs_scale_target_max_capacity = 10
app_ecs_scale_target_min_capacity = 5
app_ecs_cooldown_scale_down       = 300
app_ecs_cooldown_scale_up         = 180

cli_fargate_cpu    = "2048"
cli_fargate_memory = "8192"

batch_default_ce_spot_fleet_bid_percentage = 60
batch_ami_id                               = "ami-002e2fef4b94f8fd0"

batch_default_ce_min_vcpus = 0
batch_default_ce_max_vcpus = 128
batch_default_job_memory   = 8192

batch_default_ce_instance_types = ["c5", "m5"]

gunicorn_worker_timeout = "360"
gunicorn_workers        = "5"

ec_memcached_identifier = "opensupplyhub-prd"

rds_final_snapshot_identifier = "opensupplyhub-rds-prd"
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

instance_source = "os_hub"

vpn_ec2_ami = "ami-0940c95b23a1f7cac"

enable_homepage_proxy   = true
craft_cms_origin_domain = "open-supply.production.servd.dev"

is_database_private_link_provider = true

# Owns the shared-account Chatbot Slack channel config for Production/Staging/RBA.
# Sibling SNS ARNs live in SM (aws_chatbot_additional_sns_topic_arns_secret_name).
# Staging/RBA set aws_chatbot_manage_channel_configuration = false.
aws_chatbot_manage_channel_configuration = true

# Owns the account-level AWS Budget for Bedrock spend (account shared
# with Staging/RBA, which leave manage_bedrock_cost_budget at its
# default of false).
manage_bedrock_cost_budget = true

waf_enabled = true
memcached_view_cache_timeout_seconds = 360
stripe_price_id = "price_1TPjKeAnUgyIppdhAECREwYL"
hubspot_subscription_id = "12847627"
dromo_schema_id = "6f3e129c-d724-4b80-b2c9-8e54b47e8017"
google_drive_shared_directory_id = "12ZhHCXHJD25NbfrqGnp5AT39odskr1Si"
aws_key_name = "osh-prd"
database_anonymizer_enabled = true
anonymizer_db_identifier = "database-anonymizer"
anonymizer_schedule_expression = "cron(0 1 ? * SAT *)"
enable_legacy_info_site_redirect = true

rds_master_secret_name = "oshub/production/rds-master"
django_secret_key_secret_name = "oshub/production/django-secret-key"
cloudfront_auth_token_secret_name = "oshub/production/cloudfront-auth-token"
default_from_email_secret_name = "oshub/production/default-from-email"
data_from_email_secret_name = "oshub/production/data-from-email"
notification_email_to_secret_name = "oshub/production/notification-email-to"
claim_from_email_secret_name = "oshub/production/claim-from-email"
google_server_side_api_key_secret_name = "oshub/production/google-server-side-api-key"
google_client_side_api_key_secret_name = "oshub/production/google-client-side-api-key"
google_analytics_key_secret_name = "oshub/production/google-analytics-key"
google_service_account_creds_base64_secret_name = "oshub/production/google-service-account-creds-base64"
rollbar_server_side_access_token_secret_name = "oshub/production/rollbar-server-side-access-token"
rollbar_client_side_access_token_secret_name = "oshub/production/rollbar-client-side-access-token"
oar_client_key_secret_name = "oshub/production/oar-client-key"
hubspot_api_key_secret_name = "oshub/production/hubspot-api-key"
stripe_secret_key_secret_name = "oshub/production/stripe-secret-key"
stripe_webhook_secret_secret_name = "oshub/production/stripe-webhook-secret"
dark_visitors_token_secret_name = "oshub/production/dark-visitors-token"
dark_visitors_project_key_secret_name = "oshub/production/dark-visitors-project-key"
dromo_license_key_secret_name = "oshub/production/dromo-license-key"
external_access_cidr_blocks_secret_name = "oshub/production/external-access-cidr-blocks"
ip_denylist_secret_name = "oshub/production/ip-denylist"
aws_chatbot_additional_sns_topic_arns_secret_name = "oshub/production/aws-chatbot-additional-sns-topic-arns"
aws_chatbot_slack_config_secret_name = "oshub/production/aws-chatbot-slack-config"
vanta_assumed_role_external_ids_secret_name = "oshub/production/vanta-assumed-role-external-ids"
vanta_assumed_role_principals_secret_name = "oshub/production/vanta-assumed-role-principals"
anonymizer_destination_aws_account_secret_name = "oshub/production/anonymizer-destination-aws-account"
anonymizer_kms_key_admin_users_secret_name = "oshub/production/anonymizer-kms-key-admin-users"
contribot_os_hub_api_token_secret_name = "oshub/production/contribot-os-hub-api-token"
contribot_monday_api_key_secret_name = "oshub/production/contribot-monday-api-key"
contribot_slack_api_url_secret_name = "oshub/production/contribot-slack-api-url"
contribot_google_drive_service_key_secret_name = "oshub/production/contribot-google-drive-service-key"

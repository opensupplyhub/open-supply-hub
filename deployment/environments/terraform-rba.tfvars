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

bastion_ami           = "ami-0bb3fad3c0286ebd5"
bastion_instance_type = "t3.nano"

rds_allocated_storage      = "256"
rds_engine_version         = "16"
rds_parameter_group_family = "postgres16"
rds_instance_type          = "db.m6in.4xlarge"
rds_database_identifier    = "opensupplyhub-enc-rba"
rds_database_name          = "opensupplyhub"
rds_multi_az               = false
rds_storage_encrypted      = true

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

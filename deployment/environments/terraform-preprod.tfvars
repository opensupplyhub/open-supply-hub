project = "OpenSupplyHub" # secure
environment = "Preprod" # secure
py_environment = "Staging" # secure

aws_region = "eu-west-1" # secure
aws_availability_zones = ["eu-west-1a", "eu-west-1b"] # secure

r53_private_hosted_zone = "osh.internal" # secure
r53_service_discovery_zone = "pp.internal" # secure
r53_public_hosted_zone = "os-hub.net" # secure

cloudfront_price_class = "PriceClass_All" # secure

bastion_ami = "ami-0bb3fad3c0286ebd5" # secure
bastion_instance_type = "t3.medium" # secure

rds_allocated_storage = "128" # secure
rds_engine_version = "12" # secure
rds_parameter_group_family = "postgres12" # secure
rds_instance_type = "db.t3.2xlarge" # secure
rds_database_identifier = "opensupplyhub-enc-pp" # secure
rds_database_name = "opensupplyhub" # secure
rds_multi_az = false # secure
rds_storage_encrypted = true # secure

app_ecs_desired_count = "16" # secure
app_ecs_deployment_min_percent = "100" # secure
app_ecs_deployment_max_percent = "400" # secure
app_fargate_cpu = "2048" # secure
app_fargate_memory = "8192" # secure

cli_fargate_cpu = "2048" # secure
cli_fargate_memory = "8192" # secure

gunicorn_worker_timeout = "240" # secure

batch_default_ce_spot_fleet_bid_percentage = 60 # secure
batch_ami_id = "ami-002e2fef4b94f8fd0" # secure

batch_default_ce_min_vcpus = 0 # secure
batch_default_ce_max_vcpus = 128 # secure
batch_default_job_memory = 8192 # secure

batch_default_ce_instance_types = ["c5", "m5"] # secure

app_ecs_grace_period_seconds = 300 # secure

ec_memcached_identifier = "opensupplyhub-pp" # secure
rds_final_snapshot_identifier = "opensupplyhub-rds-pp" # secure
topic_dedup_basic_name = "basic-name" # secure
dedupe_hub_live = true # secure
dedupe_hub_name = "deduplicate" # secure
dedupe_hub_version = 1 # secure
app_cc_ecs_desired_count = 0 # secure
app_dd_fargate_cpu = 4096
app_dd_fargate_memory = 8192
app_dd_ecs_desired_count = 1
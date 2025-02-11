project = "OpenSupplyHub"
environment = "Development"

aws_region = "eu-west-1"
aws_availability_zones = ["eu-west-1a", "eu-west-1b"]

r53_private_hosted_zone = "osh.internal"
r53_service_discovery_zone = "sd.internal"
r53_public_hosted_zone = "os-hub.net"

cloudfront_price_class = "PriceClass_All"

bastion_ami = "ami-0bb3fad3c0286ebd5"
bastion_instance_type = "t3.nano"

rds_allocated_storage = "128"
rds_engine_version = "16"
rds_parameter_group_family = "postgres16"
rds_instance_type = "db.t3.micro"
rds_database_identifier = "opensupplyhub-enc-dev"
rds_database_name = "opensupplyhub"
rds_multi_az = false
rds_storage_encrypted = true
rds_allow_major_version_upgrade = true
rds_apply_immediately = true

app_ecs_desired_count = "1"
app_ecs_deployment_min_percent = "100"
app_ecs_deployment_max_percent = "200"
app_fargate_cpu = "512"
app_fargate_memory = "1024"

app_dd_fargate_cpu = "2048"
app_dd_fargate_memory = "4096"

cli_fargate_cpu = "256"
cli_fargate_memory = "1024"

gunicorn_worker_timeout = "240"

batch_default_ce_spot_fleet_bid_percentage = 60
batch_ami_id = "ami-002e2fef4b94f8fd0"

batch_default_ce_min_vcpus = 0
batch_default_ce_max_vcpus = 128
batch_default_job_memory = 8192

batch_default_ce_instance_types = ["c5", "m5"]

app_ecs_grace_period_seconds = 300

ec_memcached_identifier = "opensupplyhub-dev"
rds_final_snapshot_identifier = "opensupplyhub-rds-dev"
topic_dedup_basic_name = "basic-name"
dedupe_hub_live = true
dedupe_hub_name = "deduplicate"
dedupe_hub_version = 1
app_cc_ecs_desired_count = 1

opensearch_instance_type = "t3.small.search"

app_logstash_fargate_cpu = 256
app_logstash_fargate_memory = 2048

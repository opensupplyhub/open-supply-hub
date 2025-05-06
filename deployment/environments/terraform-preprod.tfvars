project = "OpenSupplyHub"
environment = "Preprod"

aws_region = "eu-west-1"
aws_availability_zones = ["eu-west-1a", "eu-west-1b"]

r53_private_hosted_zone = "osh.internal"
r53_service_discovery_zone = "pp.internal"
r53_public_hosted_zone = "os-hub.net"

cloudfront_price_class = "PriceClass_All"

bastion_ami = "ami-0bb3fad3c0286ebd5"
bastion_instance_type = "t3.nano"

rds_allocated_storage = "256"
rds_engine_version = "16"
rds_parameter_group_family = "postgres16"
rds_instance_type = "db.m6in.4xlarge"
rds_database_identifier = "opensupplyhub-enc-pp"
rds_database_name = "opensupplyhub"
rds_multi_az = false
rds_storage_encrypted = true
rds_skip_final_snapshot = true
rds_deletion_protection = false

app_ecs_desired_count = "10"
app_ecs_deployment_min_percent = "100"
app_ecs_deployment_max_percent = "400"
app_fargate_cpu = "2048"
app_fargate_memory = "4096"

app_ecs_max_cpu_threshold         = 85
app_ecs_min_cpu_threshold         = 15
app_ecs_scale_target_max_capacity = 10
app_ecs_scale_target_min_capacity = 5
app_ecs_cooldown_scale_down       = 300
app_ecs_cooldown_scale_up         = 180

cli_fargate_cpu = "2048"
cli_fargate_memory = "8192"

gunicorn_worker_timeout = "240"

batch_default_ce_spot_fleet_bid_percentage = 60
batch_ami_id = "ami-002e2fef4b94f8fd0"

batch_default_ce_min_vcpus = 0
batch_default_ce_max_vcpus = 128
batch_default_job_memory = 8192

batch_default_ce_instance_types = ["c5", "m5"]

app_ecs_grace_period_seconds = 300

ec_memcached_identifier = "opensupplyhub-pp"
rds_final_snapshot_identifier = "opensupplyhub-rds-pp"
topic_dedup_basic_name = "basic-name"
dedupe_hub_live = true
dedupe_hub_name = "deduplicate"
dedupe_hub_version = 1
app_cc_ecs_desired_count = 0
app_dd_fargate_cpu = 4096
app_dd_fargate_memory = 16384
app_dd_ecs_desired_count = 1

opensearch_instance_type = "m6g.large.search"

app_logstash_fargate_cpu = 256
app_logstash_fargate_memory = 2048

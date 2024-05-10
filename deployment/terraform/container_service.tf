locals {
  app_image            = "${module.ecr_repository_app.repository_url}:${var.image_tag}"
  app_cc_image         = "${module.ecr_repository_app_cc.repository_url}:${var.image_tag}"
  app_dd_image         = "${module.ecr_repository_app_dd.repository_url}:${var.image_tag}"
  app_kafka_image      = "${module.ecr_repository_kafka.repository_url}:${var.image_tag}"
  batch_job_queue_name = "queue${local.short}Default"
  batch_job_def_name   = "job${local.short}Default"

}

#
# Security Group Resources
#
resource "aws_security_group" "alb" {
  vpc_id = module.vpc.id

  tags = {
    Name        = "sgAppLoadBalancer"
    Project     = var.project
    Environment = var.environment
  }
}

resource "aws_security_group" "app" {
  vpc_id = module.vpc.id

  tags = {
    Name        = "sgAppEcsService"
    Project     = var.project
    Environment = var.environment
  }
}

resource "aws_security_group" "app_cc" {
  vpc_id = module.vpc.id

  tags = {
    Name        = "sgAppEcsService"
    Project     = var.project
    Environment = var.environment
  }
}

resource "aws_security_group" "batch" {
  vpc_id = module.vpc.id

  tags = {
    Name        = "sgBatchContainerInstance"
    Project     = var.project
    Environment = var.environment
  }
}

#
# ALB Resources
#
resource "aws_lb" "app" {
  name            = "alb${local.short}App"
  security_groups = [aws_security_group.alb.id]
  subnets         = module.vpc.public_subnet_ids

  access_logs {
    bucket  = aws_s3_bucket.logs.id
    prefix  = "ALB"
    enabled = true
  }

  tags = {
    Name        = "alb${local.short}App"
    Project     = var.project
    Environment = var.environment
  }

  # In order to enable access logging, the ELB service account needs S3 access.
  # This is a "hidden" dependency that Terraform cannot automatically infer, so
  # it must be declared explicitly.
  depends_on = [aws_s3_bucket_policy.alb_access_logging]
}

resource "aws_lb_target_group" "app" {
  name = "tg${local.short}App"

  health_check {
    healthy_threshold   = "3"
    interval            = "30"
    matcher             = "200"
    protocol            = "HTTP"
    timeout             = "3"
    path                = "/health-check/"
    unhealthy_threshold = "2"
  }

  port     = "80"
  protocol = "HTTP"
  vpc_id   = module.vpc.id

  target_type = "ip"

  tags = {
    Name        = "tg${local.short}App"
    Project     = var.project
    Environment = var.environment
  }
}

resource "aws_lb_target_group" "app_cc" {
  name = "tg${local.short}AppCC"

  health_check {
    healthy_threshold   = "3"
    interval            = "30"
    matcher             = "200"
    protocol            = "HTTP"
    timeout             = "3"
    path                = "/healthcheck"
    unhealthy_threshold = "2"
  }

  port     = "80"
  protocol = "HTTP"
  vpc_id   = module.vpc.id

  target_type = "ip"

  tags = {
    Name        = "tg${local.short}AppCC"
    Project     = var.project
    Environment = var.environment
  }
}

resource "aws_lb_listener" "app" {
  load_balancer_arn = aws_lb.app.id
  port              = "443"
  protocol          = "HTTPS"
  certificate_arn   = module.cert_lb.arn

  default_action {
    type = "fixed-response"
    fixed_response {
      content_type = "text/plain"
      status_code  = 403
      message_body = "Access denied"
    }
  }
}

resource "aws_lb_listener_rule" "cdn_auth" {
  listener_arn = aws_lb_listener.app.id
  priority     = 20

  condition {
    http_header {
      http_header_name = "X-CloudFront-Auth"
      values           = [var.cloudfront_auth_token]
    }
  }

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app.id
  }
}

resource "aws_lb_listener_rule" "cdn_auth_contricleaner" {
  listener_arn = aws_lb_listener.app.id
  priority     = 10

  condition {
    http_header {
      http_header_name = "X-CloudFront-Auth"
      values           = [var.cloudfront_auth_token]
    }
  }

  condition {
    path_pattern {
      values = ["/cc/*"]
    }
  }

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app_cc.id
  }
}

#
# ECS Resources
#
resource "aws_ecs_cluster" "app" {
  name = "ecs${local.short}Cluster"
}

data "template_file" "app" {
  template = file("task-definitions/app.json")

  vars = {
    image                            = local.app_image
    postgres_host                    = aws_route53_record.database.name
    postgres_port                    = module.database_enc.port
    postgres_user                    = var.rds_database_username
    postgres_password                = var.rds_database_password
    postgres_db                      = var.rds_database_name
    gunicorn_workers                 = 1
    gunicorn_worker_timeout          = var.gunicorn_worker_timeout
    google_server_side_api_key       = var.google_server_side_api_key
    google_client_side_api_key       = var.google_client_side_api_key
    google_analytics_key             = var.google_analytics_key
    rollbar_server_side_access_token = var.rollbar_server_side_access_token
    rollbar_client_side_access_token = var.rollbar_client_side_access_token
    django_secret_key                = var.django_secret_key
    oar_client_key                   = var.oar_client_key
    external_domain                  = local.domain_name
    default_from_email               = var.default_from_email
    data_from_email                  = var.data_from_email
    notification_email_to            = var.notification_email_to
    hubspot_api_key                  = var.hubspot_api_key
    hubspot_subscription_id          = var.hubspot_subscription_id
    app_port                         = var.app_port
    aws_region                       = var.aws_region
    project                          = var.project
    environment                      = var.environment
    py_environment                   = var.py_environment
    CORS_ALLOWED_ORIGIN_REGEXES      = var.CORS_ALLOWED_ORIGIN_REGEXES
    batch_job_queue_name             = local.batch_job_queue_name
    batch_job_def_name               = local.batch_job_def_name
    log_group_name                   = "log${local.short}App"
    cache_host                       = aws_route53_record.cache.name
    cache_port                       = var.ec_memcached_port
    aws_storage_bucket_name          = local.files_bucket_name
    claim_from_email                 = var.claim_from_email
    kafka_bootstrap_servers          = join (",", module.msk_cluster.bootstrap_brokers)
    kafka_topic_basic_name           = var.topic_dedup_basic_name
  }
}

resource "aws_ecs_task_definition" "app" {
  family                   = "${local.short}App"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.app_fargate_cpu
  memory                   = var.app_fargate_memory

  task_role_arn      = aws_iam_role.app_task_role.arn
  execution_role_arn = aws_iam_role.ecs_task_execution_role.arn

  container_definitions = data.template_file.app.rendered
}

data "template_file" "app_cli" {
  template = file("task-definitions/app_cli.json")

  vars = {
    image                            = local.app_image
    postgres_host                    = aws_route53_record.database.name
    postgres_port                    = module.database_enc.port
    postgres_user                    = var.rds_database_username
    postgres_password                = var.rds_database_password
    postgres_db                      = var.rds_database_name
    google_server_side_api_key       = var.google_server_side_api_key
    google_client_side_api_key       = var.google_client_side_api_key
    google_analytics_key             = var.google_analytics_key
    rollbar_server_side_access_token = var.rollbar_server_side_access_token
    rollbar_client_side_access_token = var.rollbar_client_side_access_token
    django_secret_key                = var.django_secret_key
    oar_client_key                   = var.oar_client_key
    external_domain                  = local.domain_name
    default_from_email               = var.default_from_email
    data_from_email                  = var.data_from_email
    notification_email_to            = var.notification_email_to
    hubspot_api_key                  = var.hubspot_api_key
    hubspot_subscription_id          = var.hubspot_subscription_id
    app_port                         = var.app_port
    aws_region                       = var.aws_region
    project                          = var.project
    environment                      = var.environment
    batch_job_queue_name             = local.batch_job_queue_name
    batch_job_def_name               = local.batch_job_def_name
    log_group_name                   = "log${local.short}AppCLI"
    cache_host                       = aws_route53_record.cache.name
    cache_port                       = var.ec_memcached_port
    aws_storage_bucket_name          = local.files_bucket_name
    kafka_bootstrap_servers          = join (",", module.msk_cluster.bootstrap_brokers)
    kafka_topic_basic_name           = var.topic_dedup_basic_name
  }
}

resource "aws_ecs_task_definition" "app_cli" {
  family                   = "${local.short}AppCLI"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.cli_fargate_cpu
  memory                   = var.cli_fargate_memory

  task_role_arn      = aws_iam_role.app_task_role.arn
  execution_role_arn = aws_iam_role.ecs_task_execution_role.arn

  container_definitions = data.template_file.app_cli.rendered
}

data "template_file" "app_cc" {
  template = file("task-definitions/app_cc.json")

  vars = {
    image          = local.app_cc_image
    api_url        = "api.${var.r53_service_discovery_zone}:8080"
    app_cc_port    = var.app_cc_port
    log_group_name = "log${local.short}AppCC"
    aws_region     = var.aws_region
  }
}

data "template_file" "app_dd" {
  template = file("task-definitions/app_dd.json")

  vars = {
    image                            = local.app_dd_image
    log_group_name                   = "log${local.short}AppDD"
    aws_region                       = var.aws_region
    postgres_host                    = aws_route53_record.database.name
    postgres_port                    = module.database_enc.port
    postgres_user                    = var.rds_database_username
    postgres_password                = var.rds_database_password
    postgres_db                      = var.rds_database_name
    env                              = "staging"
    git_commit                       = "latest"
    consumer_group_id                = var.consumer_group_id
    consumer_client_id               = var.consumer_client_id
    bootstrap_servers                = join (",", module.msk_cluster.bootstrap_brokers)
    topic_dedup_basic_name           = var.topic_dedup_basic_name
    rollbar_server_side_access_token = var.rollbar_server_side_access_token
    security_protocol                = var.security_protocol
    dedupe_hub_live                  = var.dedupe_hub_live
    dedupe_hub_name                  = var.dedupe_hub_name
    dedupe_hub_version               = var.dedupe_hub_version
  }
}


resource "aws_ecs_task_definition" "app_cc" {
  family                   = "${local.short}AppCC"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.app_cc_fargate_cpu
  memory                   = var.app_cc_fargate_memory

  task_role_arn      = aws_iam_role.app_task_role.arn
  execution_role_arn = aws_iam_role.ecs_task_execution_role.arn

  container_definitions = data.template_file.app_cc.rendered
}

resource "aws_ecs_task_definition" "app_dd" {
  family                   = "${local.short}AppDD"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.app_dd_fargate_cpu
  memory                   = var.app_dd_fargate_memory

  task_role_arn      = aws_iam_role.app_task_role.arn
  execution_role_arn = aws_iam_role.ecs_task_execution_role.arn

  container_definitions = data.template_file.app_dd.rendered
}

resource "aws_ecs_service" "app" {
  name            = "${local.short}App"
  cluster         = aws_ecs_cluster.app.id
  task_definition = aws_ecs_task_definition.app.arn

  desired_count                      = var.app_ecs_desired_count
  deployment_minimum_healthy_percent = var.app_ecs_deployment_min_percent
  deployment_maximum_percent         = var.app_ecs_deployment_max_percent
  health_check_grace_period_seconds  = var.app_ecs_grace_period_seconds

  launch_type = "FARGATE"

  network_configuration {
    security_groups = [aws_security_group.app.id]
    subnets         = module.vpc.private_subnet_ids
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.app.arn
    container_name   = "django"
    container_port   = var.app_port
  }

  service_registries {
    registry_arn = aws_service_discovery_service.app.arn
  }

  depends_on = [aws_lb_listener.app]
}

resource "aws_ecs_service" "app_cc" {
  name            = "${local.short}AppCC"
  cluster         = aws_ecs_cluster.app.id
  task_definition = aws_ecs_task_definition.app_cc.arn

  desired_count                      = var.app_cc_ecs_desired_count
  deployment_minimum_healthy_percent = var.app_cc_ecs_deployment_min_percent
  deployment_maximum_percent         = var.app_cc_ecs_deployment_max_percent
  health_check_grace_period_seconds  = var.app_cc_ecs_grace_period_seconds

  launch_type = "FARGATE"

  network_configuration {
    security_groups = [aws_security_group.app_cc.id]
    subnets         = module.vpc.private_subnet_ids
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.app_cc.arn
    container_name   = "contricleaner"
    container_port   = var.app_cc_port
  }

  depends_on = [aws_lb_listener.app]
}

resource "aws_ecs_service" "app_dd" {
  name            = "${local.short}AppDD"
  cluster         = aws_ecs_cluster.app.id
  task_definition = aws_ecs_task_definition.app_dd.arn

  desired_count                      = var.app_dd_ecs_desired_count
  deployment_minimum_healthy_percent = var.app_dd_ecs_deployment_min_percent
  deployment_maximum_percent         = var.app_dd_ecs_deployment_max_percent

  launch_type = "FARGATE"

  network_configuration {
    security_groups = [aws_security_group.app.id]
    subnets         = module.vpc.private_subnet_ids
  }
}

locals {
  broker_host_list = split(",",module.msk_cluster.bootstrap_brokers[0])
}

data "template_file" "app_kafka" {
  template = file("task-definitions/app_kafka.json")

  vars = {
    image                            = local.app_kafka_image
    log_group_name                   = "log${local.short}AppKafka"
    aws_region                       = var.aws_region
    bootstrap_servers                = local.broker_host_list[0]
    topic_dedup_basic_name           = var.topic_dedup_basic_name
  }
}

resource "aws_ecs_task_definition" "app_kafka" {
  family                   = "${local.short}AppKafka"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.cli_fargate_cpu
  memory                   = var.cli_fargate_memory

  task_role_arn      = aws_iam_role.app_task_role.arn
  execution_role_arn = aws_iam_role.ecs_task_execution_role.arn

  container_definitions = data.template_file.app_kafka.rendered
}

#
# CloudWatch Resources
#
resource "aws_cloudwatch_log_group" "app" {
  name              = "log${local.short}App"
  retention_in_days = 30
}

resource "aws_cloudwatch_log_group" "cli" {
  name              = "log${local.short}AppCLI"
  retention_in_days = 30
}

resource "aws_cloudwatch_log_group" "cc" {
  name              = "log${local.short}AppCC"
  retention_in_days = 30
}

resource "aws_cloudwatch_log_group" "dd" {
  name              = "log${local.short}AppDD"
  retention_in_days = 30
}

resource "aws_cloudwatch_log_group" "kafka" {
  name              = "log${local.short}AppKafka"
  retention_in_days = 30
}

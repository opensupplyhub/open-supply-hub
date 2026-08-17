# Bake definition for Deploy to AWS ECR image builds.
# Variables are supplied by the workflow (ECR_REGISTRY, IMAGE_NAME, ENV_SLUG, GIT_COMMIT, DOCKER_IMAGE).

variable "ECR_REGISTRY" {}
variable "IMAGE_NAME" {}
variable "ENV_SLUG" {}
variable "GIT_COMMIT" {}
variable "DOCKER_IMAGE" {
  default = ""
}

group "default" {
  targets = ["kafka", "django", "batch", "dedupe", "logstash"]
}

target "kafka" {
  context    = "src/kafka-tools"
  dockerfile = "Dockerfile"
  tags       = ["${ECR_REGISTRY}/${IMAGE_NAME}-kafka-${ENV_SLUG}:${GIT_COMMIT}"]
}

target "django" {
  context    = "src/django"
  dockerfile = "Dockerfile"
  tags       = ["${ECR_REGISTRY}/${IMAGE_NAME}-${ENV_SLUG}:${GIT_COMMIT}"]
}

target "batch" {
  context    = "src/batch"
  dockerfile = "Dockerfile"
  tags       = ["${ECR_REGISTRY}/${IMAGE_NAME}-batch-${ENV_SLUG}:${GIT_COMMIT}"]
  args = {
    GIT_COMMIT   = GIT_COMMIT
    DOCKER_IMAGE = DOCKER_IMAGE
    ENVIRONMENT  = ENV_SLUG
  }
}

target "dedupe" {
  context    = "src/dedupe-hub/api"
  dockerfile = "Dockerfile"
  tags       = ["${ECR_REGISTRY}/${IMAGE_NAME}-deduplicate-${ENV_SLUG}:${GIT_COMMIT}"]
}

target "logstash" {
  context    = "src/logstash"
  dockerfile = "Dockerfile"
  tags       = ["${ECR_REGISTRY}/${IMAGE_NAME}-logstash-${ENV_SLUG}:${GIT_COMMIT}"]
}

# Production-only
target "database-anonymizer" {
  context    = "deployment/terraform/database_anonymizer_scheduled_task/docker"
  dockerfile = "Dockerfile"
  tags       = ["${ECR_REGISTRY}/${IMAGE_NAME}-database-anonymizer-${ENV_SLUG}:${GIT_COMMIT}"]
}

# Test-only
target "anonymized-database-dump" {
  context    = "deployment/terraform/anonymized_database_dump_scheduled_task/docker"
  dockerfile = "Dockerfile"
  tags       = ["${ECR_REGISTRY}/${IMAGE_NAME}-anonymized-database-dump-${ENV_SLUG}:${GIT_COMMIT}"]
}

module "codebuild_github_runner" {
  count = var.codebuild_github_runner_enabled == true ? 1 : 0

  source = "./codebuild_github_runner"

  codebuild_project_name = var.codebuild_github_runner_project_name
  github_repository_url  = var.codebuild_github_runner_repository_url
  github_connection_arn  = var.codebuild_github_runner_connection_arn
  compute_type           = var.codebuild_github_runner_compute_type
  build_timeout          = var.codebuild_github_runner_build_timeout
  aws_region             = var.aws_region
  environment            = var.environment
  project                = var.project
}

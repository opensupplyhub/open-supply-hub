variable "project" {
  default = "Open Supply Hub"
}

variable "environment" {
  default = "Test"
}

variable "aws_region" {
  type    = string
  default = "eu-west-1"
}

variable "codebuild_project_name" {
  description = "Name of the CodeBuild project. Referenced by workflows as runs-on: codebuild-<name>-..."
  type        = string
}

variable "github_repository_url" {
  description = "HTTPS clone URL of the GitHub repository whose Actions jobs run on this project"
  type        = string
}

variable "github_connection_arn" {
  description = "ARN of the CodeConnections connection to the GitHub organization (created manually, OAuth handshake completed in the console)"
  type        = string
  sensitive   = true

  validation {
    condition     = length(var.github_connection_arn) > 0
    error_message = "codebuild_github_runner_connection_arn must be set when the CodeBuild GitHub runner is enabled. Create the CodeConnections connection manually and pass its ARN via tfvars."
  }
}

variable "compute_type" {
  description = "CodeBuild compute type; BUILD_GENERAL1_LARGE provides 8 vCPU / 16 GB RAM / 256 GB disk"
  type        = string
  default     = "BUILD_GENERAL1_LARGE"
}

variable "build_image" {
  type    = string
  default = "aws/codebuild/standard:8.0"
}

variable "build_timeout" {
  description = "Build timeout in minutes; DB dump/restore jobs run 85-150 minutes"
  type        = number
  default     = 300
}


terraform {
  required_version = ">= 1.0.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      # >= 5.91 is required by the codebuild_github_runner module:
      # WORKFLOW_JOB_QUEUED webhook filter (5.56) and CODECONNECTIONS
      # source credentials (5.91). Kept within the 5.x major version.
      version = "~> 5.91"
    }
    template = {
      source  = "hashicorp/template"
      version = "~> 2.2.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.7"
    }
  }
}

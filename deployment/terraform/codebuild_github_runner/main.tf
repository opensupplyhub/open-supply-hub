/*
 * CodeBuild project acting as an ephemeral GitHub Actions runner.
 *
 * When a workflow job with the label
 * `codebuild-<project-name>-${{ github.run_id }}-${{ github.run_attempt }}`
 * is queued, GitHub notifies CodeBuild through the webhook below, and
 * CodeBuild starts a fresh build container that registers itself as a
 * just-in-time runner, executes the job, and is destroyed afterwards.
 * See https://docs.aws.amazon.com/codebuild/latest/userguide/action-runner.html
 */

resource "aws_cloudwatch_log_group" "github_runner" {
  name              = "log${local.short}GitHubActionsRunner"
  retention_in_days = 365
}

data "aws_iam_policy_document" "github_runner_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["codebuild.amazonaws.com"]
    }
  }
}

data "aws_iam_policy_document" "github_runner" {
  statement {
    actions = [
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources = [
      aws_cloudwatch_log_group.github_runner.arn,
      "${aws_cloudwatch_log_group.github_runner.arn}:*"
    ]
  }

  # Required for CodeBuild to authenticate to GitHub through the
  # CodeConnections connection. The connection ARN must use the
  # arn:aws:codeconnections: prefix (see README).
  statement {
    actions = [
      "codeconnections:GetConnection",
      "codeconnections:GetConnectionToken",
      "codeconnections:UseConnection"
    ]
    resources = [var.github_connection_arn]
  }
}

resource "aws_iam_role" "github_runner" {
  name               = "codebuild${local.short}GitHubActionsRunner"
  assume_role_policy = data.aws_iam_policy_document.github_runner_assume_role.json
}

resource "aws_iam_role_policy" "github_runner" {
  name   = "codebuild${local.short}GitHubActionsRunnerPolicy"
  role   = aws_iam_role.github_runner.name
  policy = data.aws_iam_policy_document.github_runner.json
}

# Account-level (per region) source credential: CodeBuild uses the
# CodeConnections connection for all GitHub interactions in this region.
resource "aws_codebuild_source_credential" "github" {
  auth_type   = "CODECONNECTIONS"
  server_type = "GITHUB"
  token       = var.github_connection_arn
}

resource "aws_codebuild_project" "github_runner" {
  name           = var.codebuild_project_name
  description    = "Ephemeral GitHub Actions runner for long-running DB dump/restore workflow jobs"
  service_role   = aws_iam_role.github_runner.arn
  build_timeout  = var.build_timeout
  queued_timeout = 480

  artifacts {
    type = "NO_ARTIFACTS"
  }

  environment {
    compute_type = var.compute_type
    image        = var.build_image
    type         = "LINUX_CONTAINER"
    # Required for Docker-in-Docker: the jobs build and run the anon-tools
    # containers with the host Docker daemon.
    privileged_mode = true
  }

  source {
    type            = "GITHUB"
    location        = var.github_repository_url
    git_clone_depth = 1
    # The buildspec is ignored for runner builds: CodeBuild overrides it with
    # the GitHub Actions runner bootstrap when a workflow job is picked up.
  }

  logs_config {
    cloudwatch_logs {
      group_name = aws_cloudwatch_log_group.github_runner.name
    }
  }

  depends_on = [aws_codebuild_source_credential.github]
}

# The WORKFLOW_JOB_QUEUED filter is what turns this project into a GitHub
# Actions runner provider instead of a regular CI trigger.
resource "aws_codebuild_webhook" "github_runner" {
  project_name = aws_codebuild_project.github_runner.name
  build_type   = "BUILD"

  filter_group {
    filter {
      type    = "EVENT"
      pattern = "WORKFLOW_JOB_QUEUED"
    }
  }
}

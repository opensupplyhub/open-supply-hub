# CodeBuild GitHub Actions Runner

This module provisions an AWS CodeBuild project that acts as an **ephemeral
GitHub Actions runner** for the long-running database jobs:

- **DB - Save Anonymized DB** (`.github/workflows/db_save_anonymized.yml`)
- **DB - Apply Anonymized DB** (`.github/workflows/db_apply_anonimized.yml`)
- **Deploy to AWS** → `restore_database` job (`.github/workflows/deploy_to_aws.yml`)

## How it works

1. A workflow job declares `runs-on: codebuild-<project-name>-${{ github.run_id }}-${{ github.run_attempt }}`.
2. When the job is queued, GitHub notifies CodeBuild through the webhook
   created by this module (filter event `WORKFLOW_JOB_QUEUED`).
3. CodeBuild starts a fresh build container, which registers itself with
   GitHub as a just-in-time runner, executes the job, deregisters, and is
   destroyed. Nothing runs (and nothing is billed) between jobs.

See the [AWS documentation](https://docs.aws.amazon.com/codebuild/latest/userguide/action-runner.html) for details.

The database access pattern is unchanged: job steps still open an SSH tunnel
through the public bastion of the target environment (see
`src/anon-tools/do_dump.sh` / `do_restore.sh`). The runner only provides
compute, disk, and Docker.

Bastion reachability was verified at migration time: the SSH ingress
allowlist of each environment's bastion (`bastion_ssh_ingress` in
`deployment/terraform/firewall.tf`, with per-environment values coming from
the private tfvars) admits the runner's AWS egress IPs, so no security group
changes were needed. If those allowlists are ever tightened, attach this
CodeBuild project to the Test VPC (private subnets) so its egress goes
through the NAT gateway's stable Elastic IP, and allowlist that single
address on the bastions.

The module is enabled only in the **Test** environment
(`codebuild_github_runner_enabled = true` in
`deployment/environments/terraform-test.tfvars`); the single runner project
serves jobs targeting all environments because per-environment AWS
credentials and SSH keys come from GitHub environment secrets, not from the
runner's own account.

## One-time manual setup (before the first `terraform apply`)

Terraform cannot complete the GitHub OAuth handshake, so a CodeConnections
connection must be created manually **in the Test AWS account**:

1. In the AWS console (region `eu-west-1`), go to
   **Developer Tools → Settings → Connections** (CodeConnections, formerly
   CodeStar Connections) and click **Create connection**.
2. Choose **GitHub**, name it (e.g. `github-opensupplyhub`), and click
   **Connect to GitHub**.
3. Authorize/install the **AWS Connector for GitHub** app for the
   `opensupplyhub` organization (requires GitHub org admin rights; the
   installation can be scoped to the `open-supply-hub` repository).
4. The connection status becomes **Available**. Copy its ARN
   (`arn:aws:codeconnections:eu-west-1:<account-id>:connection/<uuid>`).
5. Set `codebuild_github_runner_connection_arn = "<the ARN>"` in the Test
   tfvars of the private `ci-deployment` repository (the deploy workflow
   concatenates it with `deployment/environments/terraform-test.tfvars`).

Also verify on GitHub that runner registration is allowed for the public
repository: the org-level runner group setting **Allow public repositories**
(Settings → Actions → Runner groups) must permit it.

## Validation runbook

1. Complete the one-time CodeConnections setup above and apply Terraform to
   Test via the **Deploy to AWS** workflow (plan, then apply).
2. Run **DB - Save Anonymized DB** with `deploy-env: Development` (lowest
   risk) and confirm the anonymized dump lands in
   `s3://oshub-dumps-anonymized/`.
3. Run **DB - Apply Anonymized DB** with `deploy-env: Test`.
4. Run **Deploy to AWS** to Test with `restore-db: true` to exercise the
   `restore_database` job.
5. During the first dump run, check disk usage in the build logs; if it fits
   comfortably within 128 GB, `codebuild_github_runner_compute_type` can be
   downgraded to `BUILD_GENERAL1_MEDIUM` to cut cost roughly in half.

Note on concurrency: CodeBuild starts one ephemeral build per queued job, so
two runs targeting the same environment would execute in parallel. Do not
trigger simultaneous dump/restore runs against the same environment.

## Renaming caution

The CodeBuild project name (`codebuild_github_runner_project_name`, default
`osh-github-actions-runner`) is referenced verbatim in the `runs-on` labels of
the three workflows above. If you rename the project, update the workflows in
the same change.

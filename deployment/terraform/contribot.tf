#
# ContriBot Secrets Manager
#
# Secrets are CLI-owned under oshub/<env>/contribot-* names (see public tfvars).
# Terraform looks them up by name in secrets.tf; it no longer creates empty
# aws_secretsmanager_secret shells (so env destroy does not delete tokens).
#
# First apply after this change: remove the old TF-managed shells from state so
# Terraform does not schedule their destroy against live secrets that may still
# hold values under the old names. Example:
#   terraform state rm \
#     aws_secretsmanager_secret.contribot_os_hub_api_token \
#     aws_secretsmanager_secret.contribot_monday_api_key \
#     aws_secretsmanager_secret.contribot_slack_api_url \
#     aws_secretsmanager_secret.contribot_google_drive_service_key
# Operators must copy values into the new oshub/<env>/contribot-* secrets
# before switching Lambdas to those ARNs.
#

#
# ContriBot DynamoDB state table
#
# One item per facility list (hash key list_id), plus a reserved __CURSOR__ item
# that stores last_list_id for O(1) resume. Facility-list items also store
# contributor_id, list_name, status, started_at, and finished_at. fetch_lists
# reads/advances the cursor and writes PENDING rows before process_list runs.
#

resource "aws_dynamodb_table" "contribot_state" {
  name         = "contribot${local.short}State"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "list_id"

  attribute {
    name = "list_id"
    type = "S"
  }

  point_in_time_recovery {
    enabled = true
  }

  server_side_encryption {
    enabled = true
  }

  tags = merge(local.default_tags, {
    Name = "contribotState"
  })
}

#
# ContriBot Secrets Manager
#
# Secret values are populated outside Terraform (e.g. AWS Console or CLI).
#

resource "aws_secretsmanager_secret" "contribot_os_hub_api_token" {
  name                    = "contribot${local.short}OsHubApiToken"
  description             = "ContriBot API token used to authenticate requests to Open Supply Hub."
  recovery_window_in_days = 0

  tags = merge(local.default_tags, {
    Name = "contribotOsHubApiToken"
  })
}

resource "aws_secretsmanager_secret" "contribot_monday_api_key" {
  name                    = "contribot${local.short}MondayApiKey"
  description             = "ContriBot API token used to post items to the Monday board."
  recovery_window_in_days = 0

  tags = merge(local.default_tags, {
    Name = "contribotMondayApiKey"
  })
}

resource "aws_secretsmanager_secret" "contribot_slack_api_url" {
  name                    = "contribot${local.short}SlackApiUrl"
  description             = "ContriBot webhook URL used to send Slack notifications."
  recovery_window_in_days = 0

  tags = merge(local.default_tags, {
    Name = "contribotSlackApiUrl"
  })
}

resource "aws_secretsmanager_secret" "contribot_google_drive_service_key" {
  name                    = "contribot${local.short}GoogleDriveServiceKey"
  description             = "ContriBot Google service account credentials used to upload reports to Google Drive."
  recovery_window_in_days = 0

  tags = merge(local.default_tags, {
    Name = "contribotGoogleDriveServiceKey"
  })
}

#
# ContriBot DynamoDB state table
#
# Tracks processed facility lists by list ID. Lambdas read this table via
# CONTRIBOT_STATE_TABLE_NAME to skip already-handled lists and resume after failures.
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

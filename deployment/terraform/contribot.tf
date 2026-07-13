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

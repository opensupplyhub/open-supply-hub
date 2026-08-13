#
# AWS Secrets Manager lookups (CLI-owned secrets).
#
# Public tfvars supply secret *names* only. Terraform resolves ARNs/values at
# plan/apply via data sources. When a *_secret_name is empty, locals fall back
# to the legacy plaintext variable for local/dev transition.
#
# count is used even for "common" secrets so plan works when names are unset.
#

# ---------------------------------------------------------------------------
# Common secrets (present in all env public tfvars)
# ---------------------------------------------------------------------------

data "aws_secretsmanager_secret" "rds_master" {
  count = var.rds_master_secret_name != "" ? 1 : 0
  name  = var.rds_master_secret_name
}

data "aws_secretsmanager_secret_version" "rds_master" {
  count     = var.rds_master_secret_name != "" ? 1 : 0
  secret_id = data.aws_secretsmanager_secret.rds_master[0].id
}

data "aws_secretsmanager_secret" "django_secret_key" {
  count = var.django_secret_key_secret_name != "" ? 1 : 0
  name  = var.django_secret_key_secret_name
}

data "aws_secretsmanager_secret_version" "django_secret_key" {
  count     = var.django_secret_key_secret_name != "" ? 1 : 0
  secret_id = data.aws_secretsmanager_secret.django_secret_key[0].id
}

data "aws_secretsmanager_secret" "cloudfront_auth_token" {
  count = var.cloudfront_auth_token_secret_name != "" ? 1 : 0
  name  = var.cloudfront_auth_token_secret_name
}

data "aws_secretsmanager_secret_version" "cloudfront_auth_token" {
  count     = var.cloudfront_auth_token_secret_name != "" ? 1 : 0
  secret_id = data.aws_secretsmanager_secret.cloudfront_auth_token[0].id
}

data "aws_secretsmanager_secret" "default_from_email" {
  count = var.default_from_email_secret_name != "" ? 1 : 0
  name  = var.default_from_email_secret_name
}

data "aws_secretsmanager_secret_version" "default_from_email" {
  count     = var.default_from_email_secret_name != "" ? 1 : 0
  secret_id = data.aws_secretsmanager_secret.default_from_email[0].id
}

data "aws_secretsmanager_secret" "data_from_email" {
  count = var.data_from_email_secret_name != "" ? 1 : 0
  name  = var.data_from_email_secret_name
}

data "aws_secretsmanager_secret_version" "data_from_email" {
  count     = var.data_from_email_secret_name != "" ? 1 : 0
  secret_id = data.aws_secretsmanager_secret.data_from_email[0].id
}

data "aws_secretsmanager_secret" "notification_email_to" {
  count = var.notification_email_to_secret_name != "" ? 1 : 0
  name  = var.notification_email_to_secret_name
}

data "aws_secretsmanager_secret_version" "notification_email_to" {
  count     = var.notification_email_to_secret_name != "" ? 1 : 0
  secret_id = data.aws_secretsmanager_secret.notification_email_to[0].id
}

data "aws_secretsmanager_secret" "claim_from_email" {
  count = var.claim_from_email_secret_name != "" ? 1 : 0
  name  = var.claim_from_email_secret_name
}

data "aws_secretsmanager_secret_version" "claim_from_email" {
  count     = var.claim_from_email_secret_name != "" ? 1 : 0
  secret_id = data.aws_secretsmanager_secret.claim_from_email[0].id
}

data "aws_secretsmanager_secret" "google_server_side_api_key" {
  count = var.google_server_side_api_key_secret_name != "" ? 1 : 0
  name  = var.google_server_side_api_key_secret_name
}

data "aws_secretsmanager_secret_version" "google_server_side_api_key" {
  count     = var.google_server_side_api_key_secret_name != "" ? 1 : 0
  secret_id = data.aws_secretsmanager_secret.google_server_side_api_key[0].id
}

data "aws_secretsmanager_secret" "google_client_side_api_key" {
  count = var.google_client_side_api_key_secret_name != "" ? 1 : 0
  name  = var.google_client_side_api_key_secret_name
}

data "aws_secretsmanager_secret_version" "google_client_side_api_key" {
  count     = var.google_client_side_api_key_secret_name != "" ? 1 : 0
  secret_id = data.aws_secretsmanager_secret.google_client_side_api_key[0].id
}

data "aws_secretsmanager_secret" "google_service_account_creds_base64" {
  count = var.google_service_account_creds_base64_secret_name != "" ? 1 : 0
  name  = var.google_service_account_creds_base64_secret_name
}

data "aws_secretsmanager_secret_version" "google_service_account_creds_base64" {
  count     = var.google_service_account_creds_base64_secret_name != "" ? 1 : 0
  secret_id = data.aws_secretsmanager_secret.google_service_account_creds_base64[0].id
}

data "aws_secretsmanager_secret" "rollbar_server_side_access_token" {
  count = var.rollbar_server_side_access_token_secret_name != "" ? 1 : 0
  name  = var.rollbar_server_side_access_token_secret_name
}

data "aws_secretsmanager_secret_version" "rollbar_server_side_access_token" {
  count     = var.rollbar_server_side_access_token_secret_name != "" ? 1 : 0
  secret_id = data.aws_secretsmanager_secret.rollbar_server_side_access_token[0].id
}

data "aws_secretsmanager_secret" "rollbar_client_side_access_token" {
  count = var.rollbar_client_side_access_token_secret_name != "" ? 1 : 0
  name  = var.rollbar_client_side_access_token_secret_name
}

data "aws_secretsmanager_secret_version" "rollbar_client_side_access_token" {
  count     = var.rollbar_client_side_access_token_secret_name != "" ? 1 : 0
  secret_id = data.aws_secretsmanager_secret.rollbar_client_side_access_token[0].id
}

data "aws_secretsmanager_secret" "oar_client_key" {
  count = var.oar_client_key_secret_name != "" ? 1 : 0
  name  = var.oar_client_key_secret_name
}

data "aws_secretsmanager_secret_version" "oar_client_key" {
  count     = var.oar_client_key_secret_name != "" ? 1 : 0
  secret_id = data.aws_secretsmanager_secret.oar_client_key[0].id
}

data "aws_secretsmanager_secret" "stripe_secret_key" {
  count = var.stripe_secret_key_secret_name != "" ? 1 : 0
  name  = var.stripe_secret_key_secret_name
}

data "aws_secretsmanager_secret_version" "stripe_secret_key" {
  count     = var.stripe_secret_key_secret_name != "" ? 1 : 0
  secret_id = data.aws_secretsmanager_secret.stripe_secret_key[0].id
}

data "aws_secretsmanager_secret" "stripe_webhook_secret" {
  count = var.stripe_webhook_secret_secret_name != "" ? 1 : 0
  name  = var.stripe_webhook_secret_secret_name
}

data "aws_secretsmanager_secret_version" "stripe_webhook_secret" {
  count     = var.stripe_webhook_secret_secret_name != "" ? 1 : 0
  secret_id = data.aws_secretsmanager_secret.stripe_webhook_secret[0].id
}

data "aws_secretsmanager_secret" "dark_visitors_token" {
  count = var.dark_visitors_token_secret_name != "" ? 1 : 0
  name  = var.dark_visitors_token_secret_name
}

data "aws_secretsmanager_secret_version" "dark_visitors_token" {
  count     = var.dark_visitors_token_secret_name != "" ? 1 : 0
  secret_id = data.aws_secretsmanager_secret.dark_visitors_token[0].id
}

data "aws_secretsmanager_secret" "dark_visitors_project_key" {
  count = var.dark_visitors_project_key_secret_name != "" ? 1 : 0
  name  = var.dark_visitors_project_key_secret_name
}

data "aws_secretsmanager_secret_version" "dark_visitors_project_key" {
  count     = var.dark_visitors_project_key_secret_name != "" ? 1 : 0
  secret_id = data.aws_secretsmanager_secret.dark_visitors_project_key[0].id
}

data "aws_secretsmanager_secret" "dromo_license_key" {
  count = var.dromo_license_key_secret_name != "" ? 1 : 0
  name  = var.dromo_license_key_secret_name
}

data "aws_secretsmanager_secret_version" "dromo_license_key" {
  count     = var.dromo_license_key_secret_name != "" ? 1 : 0
  secret_id = data.aws_secretsmanager_secret.dromo_license_key[0].id
}

data "aws_secretsmanager_secret" "external_access_cidr_blocks" {
  count = var.external_access_cidr_blocks_secret_name != "" ? 1 : 0
  name  = var.external_access_cidr_blocks_secret_name
}

data "aws_secretsmanager_secret_version" "external_access_cidr_blocks" {
  count     = var.external_access_cidr_blocks_secret_name != "" ? 1 : 0
  secret_id = data.aws_secretsmanager_secret.external_access_cidr_blocks[0].id
}

data "aws_secretsmanager_secret" "contribot_os_hub_api_token" {
  count = var.contribot_os_hub_api_token_secret_name != "" ? 1 : 0
  name  = var.contribot_os_hub_api_token_secret_name
}

data "aws_secretsmanager_secret" "contribot_monday_api_key" {
  count = var.contribot_monday_api_key_secret_name != "" ? 1 : 0
  name  = var.contribot_monday_api_key_secret_name
}

data "aws_secretsmanager_secret" "contribot_slack_api_url" {
  count = var.contribot_slack_api_url_secret_name != "" ? 1 : 0
  name  = var.contribot_slack_api_url_secret_name
}

data "aws_secretsmanager_secret" "contribot_google_drive_service_key" {
  count = var.contribot_google_drive_service_key_secret_name != "" ? 1 : 0
  name  = var.contribot_google_drive_service_key_secret_name
}

# ---------------------------------------------------------------------------
# Optional / env-specific secrets
# ---------------------------------------------------------------------------

data "aws_secretsmanager_secret" "google_analytics_key" {
  count = var.google_analytics_key_secret_name != "" ? 1 : 0
  name  = var.google_analytics_key_secret_name
}

data "aws_secretsmanager_secret_version" "google_analytics_key" {
  count     = var.google_analytics_key_secret_name != "" ? 1 : 0
  secret_id = data.aws_secretsmanager_secret.google_analytics_key[0].id
}

data "aws_secretsmanager_secret" "hubspot_api_key" {
  count = var.hubspot_api_key_secret_name != "" ? 1 : 0
  name  = var.hubspot_api_key_secret_name
}

data "aws_secretsmanager_secret_version" "hubspot_api_key" {
  count     = var.hubspot_api_key_secret_name != "" ? 1 : 0
  secret_id = data.aws_secretsmanager_secret.hubspot_api_key[0].id
}

data "aws_secretsmanager_secret" "ip_denylist" {
  count = var.ip_denylist_secret_name != "" ? 1 : 0
  name  = var.ip_denylist_secret_name
}

data "aws_secretsmanager_secret_version" "ip_denylist" {
  count     = var.ip_denylist_secret_name != "" ? 1 : 0
  secret_id = data.aws_secretsmanager_secret.ip_denylist[0].id
}

data "aws_secretsmanager_secret" "ip_whitelist" {
  count = var.ip_whitelist_secret_name != "" ? 1 : 0
  name  = var.ip_whitelist_secret_name
}

data "aws_secretsmanager_secret_version" "ip_whitelist" {
  count     = var.ip_whitelist_secret_name != "" ? 1 : 0
  secret_id = data.aws_secretsmanager_secret.ip_whitelist[0].id
}

data "aws_secretsmanager_secret" "anonymized_database_name" {
  count = var.anonymized_database_name_secret_name != "" ? 1 : 0
  name  = var.anonymized_database_name_secret_name
}

data "aws_secretsmanager_secret_version" "anonymized_database_name" {
  count     = var.anonymized_database_name_secret_name != "" ? 1 : 0
  secret_id = data.aws_secretsmanager_secret.anonymized_database_name[0].id
}

data "aws_secretsmanager_secret" "anonymized_database_username" {
  count = var.anonymized_database_username_secret_name != "" ? 1 : 0
  name  = var.anonymized_database_username_secret_name
}

data "aws_secretsmanager_secret_version" "anonymized_database_username" {
  count     = var.anonymized_database_username_secret_name != "" ? 1 : 0
  secret_id = data.aws_secretsmanager_secret.anonymized_database_username[0].id
}

data "aws_secretsmanager_secret" "anonymized_database_password" {
  count = var.anonymized_database_password_secret_name != "" ? 1 : 0
  name  = var.anonymized_database_password_secret_name
}

data "aws_secretsmanager_secret_version" "anonymized_database_password" {
  count     = var.anonymized_database_password_secret_name != "" ? 1 : 0
  secret_id = data.aws_secretsmanager_secret.anonymized_database_password[0].id
}

data "aws_secretsmanager_secret" "anonymized_database_kms_key_id" {
  count = var.anonymized_database_kms_key_id_secret_name != "" ? 1 : 0
  name  = var.anonymized_database_kms_key_id_secret_name
}

data "aws_secretsmanager_secret_version" "anonymized_database_kms_key_id" {
  count     = var.anonymized_database_kms_key_id_secret_name != "" ? 1 : 0
  secret_id = data.aws_secretsmanager_secret.anonymized_database_kms_key_id[0].id
}

data "aws_secretsmanager_secret" "codebuild_github_runner_connection" {
  count = var.codebuild_github_runner_connection_secret_name != "" ? 1 : 0
  name  = var.codebuild_github_runner_connection_secret_name
}

data "aws_secretsmanager_secret_version" "codebuild_github_runner_connection" {
  count     = var.codebuild_github_runner_connection_secret_name != "" ? 1 : 0
  secret_id = data.aws_secretsmanager_secret.codebuild_github_runner_connection[0].id
}

data "aws_secretsmanager_secret" "aws_chatbot_additional_sns_topic_arns" {
  count = var.aws_chatbot_additional_sns_topic_arns_secret_name != "" ? 1 : 0
  name  = var.aws_chatbot_additional_sns_topic_arns_secret_name
}

data "aws_secretsmanager_secret_version" "aws_chatbot_additional_sns_topic_arns" {
  count     = var.aws_chatbot_additional_sns_topic_arns_secret_name != "" ? 1 : 0
  secret_id = data.aws_secretsmanager_secret.aws_chatbot_additional_sns_topic_arns[0].id
}

data "aws_secretsmanager_secret" "vanta_assumed_role_external_ids" {
  count = var.vanta_assumed_role_external_ids_secret_name != "" ? 1 : 0
  name  = var.vanta_assumed_role_external_ids_secret_name
}

data "aws_secretsmanager_secret_version" "vanta_assumed_role_external_ids" {
  count     = var.vanta_assumed_role_external_ids_secret_name != "" ? 1 : 0
  secret_id = data.aws_secretsmanager_secret.vanta_assumed_role_external_ids[0].id
}

data "aws_secretsmanager_secret" "vanta_assumed_role_principals" {
  count = var.vanta_assumed_role_principals_secret_name != "" ? 1 : 0
  name  = var.vanta_assumed_role_principals_secret_name
}

data "aws_secretsmanager_secret_version" "vanta_assumed_role_principals" {
  count     = var.vanta_assumed_role_principals_secret_name != "" ? 1 : 0
  secret_id = data.aws_secretsmanager_secret.vanta_assumed_role_principals[0].id
}

data "aws_secretsmanager_secret" "anonymizer_destination_aws_account" {
  count = var.anonymizer_destination_aws_account_secret_name != "" ? 1 : 0
  name  = var.anonymizer_destination_aws_account_secret_name
}

data "aws_secretsmanager_secret_version" "anonymizer_destination_aws_account" {
  count     = var.anonymizer_destination_aws_account_secret_name != "" ? 1 : 0
  secret_id = data.aws_secretsmanager_secret.anonymizer_destination_aws_account[0].id
}

data "aws_secretsmanager_secret" "anonymizer_kms_key_admin_users" {
  count = var.anonymizer_kms_key_admin_users_secret_name != "" ? 1 : 0
  name  = var.anonymizer_kms_key_admin_users_secret_name
}

data "aws_secretsmanager_secret_version" "anonymizer_kms_key_admin_users" {
  count     = var.anonymizer_kms_key_admin_users_secret_name != "" ? 1 : 0
  secret_id = data.aws_secretsmanager_secret.anonymizer_kms_key_admin_users[0].id
}

data "aws_secretsmanager_secret" "source_db_name" {
  count = var.source_db_name_secret_name != "" ? 1 : 0
  name  = var.source_db_name_secret_name
}

data "aws_secretsmanager_secret_version" "source_db_name" {
  count     = var.source_db_name_secret_name != "" ? 1 : 0
  secret_id = data.aws_secretsmanager_secret.source_db_name[0].id
}

data "aws_secretsmanager_secret" "source_db_user" {
  count = var.source_db_user_secret_name != "" ? 1 : 0
  name  = var.source_db_user_secret_name
}

data "aws_secretsmanager_secret_version" "source_db_user" {
  count     = var.source_db_user_secret_name != "" ? 1 : 0
  secret_id = data.aws_secretsmanager_secret.source_db_user[0].id
}

data "aws_secretsmanager_secret" "source_db_password" {
  count = var.source_db_password_secret_name != "" ? 1 : 0
  name  = var.source_db_password_secret_name
}

data "aws_secretsmanager_secret_version" "source_db_password" {
  count     = var.source_db_password_secret_name != "" ? 1 : 0
  secret_id = data.aws_secretsmanager_secret.source_db_password[0].id
}

data "aws_secretsmanager_secret" "source_db_port" {
  count = var.source_db_port_secret_name != "" ? 1 : 0
  name  = var.source_db_port_secret_name
}

data "aws_secretsmanager_secret_version" "source_db_port" {
  count     = var.source_db_port_secret_name != "" ? 1 : 0
  secret_id = data.aws_secretsmanager_secret.source_db_port[0].id
}

data "aws_secretsmanager_secret" "database_private_link_vpc_endpoint_service_name" {
  count = var.database_private_link_vpc_endpoint_service_name_secret_name != "" ? 1 : 0
  name  = var.database_private_link_vpc_endpoint_service_name_secret_name
}

data "aws_secretsmanager_secret_version" "database_private_link_vpc_endpoint_service_name" {
  count     = var.database_private_link_vpc_endpoint_service_name_secret_name != "" ? 1 : 0
  secret_id = data.aws_secretsmanager_secret.database_private_link_vpc_endpoint_service_name[0].id
}

data "aws_secretsmanager_secret" "email_anonymization_secret" {
  count = var.email_anonymization_secret_secret_name != "" ? 1 : 0
  name  = var.email_anonymization_secret_secret_name
}

data "aws_secretsmanager_secret_version" "email_anonymization_secret" {
  count     = var.email_anonymization_secret_secret_name != "" ? 1 : 0
  secret_id = data.aws_secretsmanager_secret.email_anonymization_secret[0].id
}

# ---------------------------------------------------------------------------
# Resolved values and ARNs
# ---------------------------------------------------------------------------

locals {
  rds_master = var.rds_master_secret_name != "" ? jsondecode(data.aws_secretsmanager_secret_version.rds_master[0].secret_string) : {
    username = var.rds_database_username
    password = var.rds_database_password
  }

  rds_master_secret_arn = var.rds_master_secret_name != "" ? data.aws_secretsmanager_secret.rds_master[0].arn : ""
  rds_database_username = local.rds_master.username
  rds_database_password = local.rds_master.password

  django_secret_key     = var.django_secret_key_secret_name != "" ? data.aws_secretsmanager_secret_version.django_secret_key[0].secret_string : var.django_secret_key
  django_secret_key_arn = var.django_secret_key_secret_name != "" ? data.aws_secretsmanager_secret.django_secret_key[0].arn : ""

  cloudfront_auth_token = var.cloudfront_auth_token_secret_name != "" ? data.aws_secretsmanager_secret_version.cloudfront_auth_token[0].secret_string : var.cloudfront_auth_token

  default_from_email     = var.default_from_email_secret_name != "" ? data.aws_secretsmanager_secret_version.default_from_email[0].secret_string : var.default_from_email
  default_from_email_arn = var.default_from_email_secret_name != "" ? data.aws_secretsmanager_secret.default_from_email[0].arn : ""

  data_from_email     = var.data_from_email_secret_name != "" ? data.aws_secretsmanager_secret_version.data_from_email[0].secret_string : var.data_from_email
  data_from_email_arn = var.data_from_email_secret_name != "" ? data.aws_secretsmanager_secret.data_from_email[0].arn : ""

  notification_email_to     = var.notification_email_to_secret_name != "" ? data.aws_secretsmanager_secret_version.notification_email_to[0].secret_string : var.notification_email_to
  notification_email_to_arn = var.notification_email_to_secret_name != "" ? data.aws_secretsmanager_secret.notification_email_to[0].arn : ""

  claim_from_email     = var.claim_from_email_secret_name != "" ? data.aws_secretsmanager_secret_version.claim_from_email[0].secret_string : var.claim_from_email
  claim_from_email_arn = var.claim_from_email_secret_name != "" ? data.aws_secretsmanager_secret.claim_from_email[0].arn : ""

  google_server_side_api_key     = var.google_server_side_api_key_secret_name != "" ? data.aws_secretsmanager_secret_version.google_server_side_api_key[0].secret_string : var.google_server_side_api_key
  google_server_side_api_key_arn = var.google_server_side_api_key_secret_name != "" ? data.aws_secretsmanager_secret.google_server_side_api_key[0].arn : ""

  google_client_side_api_key     = var.google_client_side_api_key_secret_name != "" ? data.aws_secretsmanager_secret_version.google_client_side_api_key[0].secret_string : var.google_client_side_api_key
  google_client_side_api_key_arn = var.google_client_side_api_key_secret_name != "" ? data.aws_secretsmanager_secret.google_client_side_api_key[0].arn : ""

  google_analytics_key     = var.google_analytics_key_secret_name != "" ? data.aws_secretsmanager_secret_version.google_analytics_key[0].secret_string : var.google_analytics_key
  google_analytics_key_arn = var.google_analytics_key_secret_name != "" ? data.aws_secretsmanager_secret.google_analytics_key[0].arn : ""

  google_service_account_creds_base64     = var.google_service_account_creds_base64_secret_name != "" ? data.aws_secretsmanager_secret_version.google_service_account_creds_base64[0].secret_string : var.google_service_account_creds_base64
  google_service_account_creds_base64_arn = var.google_service_account_creds_base64_secret_name != "" ? data.aws_secretsmanager_secret.google_service_account_creds_base64[0].arn : ""

  rollbar_server_side_access_token     = var.rollbar_server_side_access_token_secret_name != "" ? data.aws_secretsmanager_secret_version.rollbar_server_side_access_token[0].secret_string : var.rollbar_server_side_access_token
  rollbar_server_side_access_token_arn = var.rollbar_server_side_access_token_secret_name != "" ? data.aws_secretsmanager_secret.rollbar_server_side_access_token[0].arn : ""

  rollbar_client_side_access_token     = var.rollbar_client_side_access_token_secret_name != "" ? data.aws_secretsmanager_secret_version.rollbar_client_side_access_token[0].secret_string : var.rollbar_client_side_access_token
  rollbar_client_side_access_token_arn = var.rollbar_client_side_access_token_secret_name != "" ? data.aws_secretsmanager_secret.rollbar_client_side_access_token[0].arn : ""

  oar_client_key     = var.oar_client_key_secret_name != "" ? data.aws_secretsmanager_secret_version.oar_client_key[0].secret_string : var.oar_client_key
  oar_client_key_arn = var.oar_client_key_secret_name != "" ? data.aws_secretsmanager_secret.oar_client_key[0].arn : ""

  hubspot_api_key     = var.hubspot_api_key_secret_name != "" ? data.aws_secretsmanager_secret_version.hubspot_api_key[0].secret_string : var.hubspot_api_key
  hubspot_api_key_arn = var.hubspot_api_key_secret_name != "" ? data.aws_secretsmanager_secret.hubspot_api_key[0].arn : ""

  stripe_secret_key     = var.stripe_secret_key_secret_name != "" ? data.aws_secretsmanager_secret_version.stripe_secret_key[0].secret_string : var.stripe_secret_key
  stripe_secret_key_arn = var.stripe_secret_key_secret_name != "" ? data.aws_secretsmanager_secret.stripe_secret_key[0].arn : ""

  stripe_webhook_secret     = var.stripe_webhook_secret_secret_name != "" ? data.aws_secretsmanager_secret_version.stripe_webhook_secret[0].secret_string : var.stripe_webhook_secret
  stripe_webhook_secret_arn = var.stripe_webhook_secret_secret_name != "" ? data.aws_secretsmanager_secret.stripe_webhook_secret[0].arn : ""

  dark_visitors_token     = var.dark_visitors_token_secret_name != "" ? data.aws_secretsmanager_secret_version.dark_visitors_token[0].secret_string : var.dark_visitors_token
  dark_visitors_token_arn = var.dark_visitors_token_secret_name != "" ? data.aws_secretsmanager_secret.dark_visitors_token[0].arn : ""

  dark_visitors_project_key     = var.dark_visitors_project_key_secret_name != "" ? data.aws_secretsmanager_secret_version.dark_visitors_project_key[0].secret_string : var.dark_visitors_project_key
  dark_visitors_project_key_arn = var.dark_visitors_project_key_secret_name != "" ? data.aws_secretsmanager_secret.dark_visitors_project_key[0].arn : ""

  dromo_license_key     = var.dromo_license_key_secret_name != "" ? data.aws_secretsmanager_secret_version.dromo_license_key[0].secret_string : var.dromo_license_key
  dromo_license_key_arn = var.dromo_license_key_secret_name != "" ? data.aws_secretsmanager_secret.dromo_license_key[0].arn : ""

  external_access_cidr_blocks = var.external_access_cidr_blocks_secret_name != "" ? jsondecode(data.aws_secretsmanager_secret_version.external_access_cidr_blocks[0].secret_string) : var.external_access_cidr_blocks

  ip_denylist  = var.ip_denylist_secret_name != "" ? jsondecode(data.aws_secretsmanager_secret_version.ip_denylist[0].secret_string) : var.ip_denylist
  ip_whitelist = var.ip_whitelist_secret_name != "" ? jsondecode(data.aws_secretsmanager_secret_version.ip_whitelist[0].secret_string) : var.ip_whitelist

  anonymized_database_name         = var.anonymized_database_name_secret_name != "" ? data.aws_secretsmanager_secret_version.anonymized_database_name[0].secret_string : var.anonymized_database_name
  anonymized_database_name_arn     = var.anonymized_database_name_secret_name != "" ? data.aws_secretsmanager_secret.anonymized_database_name[0].arn : ""
  anonymized_database_username     = var.anonymized_database_username_secret_name != "" ? data.aws_secretsmanager_secret_version.anonymized_database_username[0].secret_string : var.anonymized_database_username
  anonymized_database_username_arn = var.anonymized_database_username_secret_name != "" ? data.aws_secretsmanager_secret.anonymized_database_username[0].arn : ""
  anonymized_database_password     = var.anonymized_database_password_secret_name != "" ? data.aws_secretsmanager_secret_version.anonymized_database_password[0].secret_string : var.anonymized_database_password
  anonymized_database_password_arn = var.anonymized_database_password_secret_name != "" ? data.aws_secretsmanager_secret.anonymized_database_password[0].arn : ""
  anonymized_database_kms_key_id   = var.anonymized_database_kms_key_id_secret_name != "" ? data.aws_secretsmanager_secret_version.anonymized_database_kms_key_id[0].secret_string : var.anonymized_database_kms_key_id

  codebuild_github_runner_connection_arn = var.codebuild_github_runner_connection_secret_name != "" ? data.aws_secretsmanager_secret_version.codebuild_github_runner_connection[0].secret_string : var.codebuild_github_runner_connection_arn

  aws_chatbot_additional_sns_topic_arns = var.aws_chatbot_additional_sns_topic_arns_secret_name != "" ? jsondecode(data.aws_secretsmanager_secret_version.aws_chatbot_additional_sns_topic_arns[0].secret_string) : var.aws_chatbot_additional_sns_topic_arns

  vanta_assumed_role_external_ids = var.vanta_assumed_role_external_ids_secret_name != "" ? jsondecode(data.aws_secretsmanager_secret_version.vanta_assumed_role_external_ids[0].secret_string) : var.vanta_assumed_role_external_ids
  vanta_assumed_role_principals   = var.vanta_assumed_role_principals_secret_name != "" ? jsondecode(data.aws_secretsmanager_secret_version.vanta_assumed_role_principals[0].secret_string) : var.vanta_assumed_role_principals

  anonymizer_destination_aws_account = var.anonymizer_destination_aws_account_secret_name != "" ? data.aws_secretsmanager_secret_version.anonymizer_destination_aws_account[0].secret_string : var.anonymizer_destination_aws_account
  anonymizer_kms_key_admin_users     = var.anonymizer_kms_key_admin_users_secret_name != "" ? jsondecode(data.aws_secretsmanager_secret_version.anonymizer_kms_key_admin_users[0].secret_string) : var.anonymizer_kms_key_admin_users

  source_db_name     = var.source_db_name_secret_name != "" ? data.aws_secretsmanager_secret_version.source_db_name[0].secret_string : var.source_db_name
  source_db_user     = var.source_db_user_secret_name != "" ? data.aws_secretsmanager_secret_version.source_db_user[0].secret_string : var.source_db_user
  source_db_password = var.source_db_password_secret_name != "" ? data.aws_secretsmanager_secret_version.source_db_password[0].secret_string : var.source_db_password
  source_db_port     = var.source_db_port_secret_name != "" ? tonumber(data.aws_secretsmanager_secret_version.source_db_port[0].secret_string) : var.source_db_port

  database_private_link_vpc_endpoint_service_name = var.database_private_link_vpc_endpoint_service_name_secret_name != "" ? data.aws_secretsmanager_secret_version.database_private_link_vpc_endpoint_service_name[0].secret_string : var.database_private_link_vpc_endpoint_service_name

  email_anonymization_secret     = var.email_anonymization_secret_secret_name != "" ? data.aws_secretsmanager_secret_version.email_anonymization_secret[0].secret_string : var.email_anonymization_secret
  email_anonymization_secret_arn = var.email_anonymization_secret_secret_name != "" ? data.aws_secretsmanager_secret.email_anonymization_secret[0].arn : ""

  contribot_os_hub_api_token_arn         = var.contribot_os_hub_api_token_secret_name != "" ? data.aws_secretsmanager_secret.contribot_os_hub_api_token[0].arn : ""
  contribot_monday_api_key_arn           = var.contribot_monday_api_key_secret_name != "" ? data.aws_secretsmanager_secret.contribot_monday_api_key[0].arn : ""
  contribot_slack_api_url_arn            = var.contribot_slack_api_url_secret_name != "" ? data.aws_secretsmanager_secret.contribot_slack_api_url[0].arn : ""
  contribot_google_drive_service_key_arn = var.contribot_google_drive_service_key_secret_name != "" ? data.aws_secretsmanager_secret.contribot_google_drive_service_key[0].arn : ""

  # ARNs granted to ECS/Batch execution roles for valueFrom injection.
  ecs_secretsmanager_secret_arns = compact([
    local.rds_master_secret_arn,
    local.django_secret_key_arn,
    local.default_from_email_arn,
    local.data_from_email_arn,
    local.notification_email_to_arn,
    local.claim_from_email_arn,
    local.google_server_side_api_key_arn,
    local.google_client_side_api_key_arn,
    local.google_service_account_creds_base64_arn,
    local.oar_client_key_arn,
    local.email_anonymization_secret_arn,
    local.anonymized_database_password_arn,
    local.anonymized_database_name_arn,
    local.anonymized_database_username_arn,
  ])
}

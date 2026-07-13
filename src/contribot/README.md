# ContriBot Lambda Functions

In this directory you'll find Lambda functions that validate list uploads.

The current process consists of the following three steps:

1. Fetch newly processed lists and queue them for processing. Lists are retrieved via the `GET /api/admin-facility-lists/` endpoint.
2. For each list, download the file from S3, run the ContriCleaner report, and upload the report to Google Drive.
3. Send notifications to Slack and Monday so that data moderators can review the report.

The solution leverages AWS Step Functions to orchestrate these steps. Each step is implemented as a Lambda task; processing individual lists runs in a Map state over the newly fetched lists.

The following environment variables are required:

### Secrets Manager

Store sensitive values in AWS Secrets Manager and inject them at runtime:

1. `OS_HUB_API_TOKEN` — API token used to authenticate requests to Open Supply Hub.
2. `MONDAY_API_KEY` — API token used to post items to the Monday board.
3. `SLACK_API_URL` — Webhook URL used to send Slack notifications.
4. `GOOGLE_DRIVE_SERVICE_KEY` — Google service account credentials used to upload reports to Google Drive.

### Environment Variables

Nonsensitive configuration can be set as plain Lambda environment variables:

1. `OS_HUB_API_URL` — Base URL of the Open Supply Hub API.
2. `MONDAY_API_URL` — Base URL of the Monday.com API.
3. `AWS_STORAGE_BUCKET_NAME` — S3 bucket where uploaded facility list files are stored.
4. `GOOGLE_DRIVE_SHARED_DIRECTORY_ID` — Google Drive folder ID where ContriCleaner reports are uploaded.
5. `MONDAY_BOARD_ID` — ID of the Monday board to post the update.

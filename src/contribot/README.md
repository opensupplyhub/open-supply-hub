# ContriBot Lambda Functions

Lambda functions that validate facility list uploads and notify data moderators when reports are ready for review.

## Overview

ContriBot polls Open Supply Hub for newly processed facility lists, validates facility list uploads, uploads the annotated reports to Google Drive, and notifies moderators via Slack and Monday.

## Facility List Validation

Facility list validation is implemented in [`lib/contribot.py`](lib/contribot.py). The `ContriBot` class reads a contributor Excel workbook, runs table- and column-level quality checks (missing columns, bad countries, whitespace issues, duplicate rows, and more), applies optional auto-fixes, and writes an annotated output workbook with **Summary**, **Findings**, **Similarities**, and **Fixes** sheets. Findings are driven by error codes in a configuration workbook (`0000.error_codes.xlsx`).

Run the unit tests locally:

```bash
cd src/contribot/lib && python -m pytest tests/test_contribot.py
```

## Lambda Source Code

Handler code lives under `src/contribot/`. Each Lambda is a single `handler.py` module packaged into a zip for deployment.

| Lambda         | Handler source                                       | Deployment package                                                                                                                     |
| -------------- | ---------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| `fetch_lists`  | [`fetch_lists/handler.py`](fetch_lists/handler.py)   | [`deployment/terraform/lambda-functions/contribot_fetch_lists/`](../../deployment/terraform/lambda-functions/contribot_fetch_lists/)   |
| `process_list` | [`process_list/handler.py`](process_list/handler.py) | [`deployment/terraform/lambda-functions/contribot_process_list/`](../../deployment/terraform/lambda-functions/contribot_process_list/) |
| `notify`       | [`notify/handler.py`](notify/handler.py)             | [`deployment/terraform/lambda-functions/contribot_notify/`](../../deployment/terraform/lambda-functions/contribot_notify/)             |

Shared Python dependencies are listed in [`requirements.txt`](requirements.txt) (runtime) and [`requirements-dev.txt`](requirements-dev.txt) (local development).

Build all deployment zips from this directory:

```bash
make -C src/contribot
```

Each package Makefile zips its handler into `deployment/terraform/lambda-functions/<name>/<name>.zip`. Terraform defines the Lambda resources in [`deployment/terraform/contribot_lambda.tf`](../../deployment/terraform/contribot_lambda.tf); the Step Functions workflow is in [`deployment/terraform/step-functions/contribot.json`](../../deployment/terraform/step-functions/contribot.json) and [`deployment/terraform/contribot_sfn.tf`](../../deployment/terraform/contribot_sfn.tf).

## Architecture

The solution leverages **AWS Step Functions** to orchestrate the workflow. Each step is implemented as a Lambda task; processing individual lists runs in a **Map** state over the newly fetched lists.

**DynamoDB** stores the state of processed lists so scheduled runs can skip lists that were already handled and resume safely after failures.

```mermaid
flowchart LR
  SFN[Step Functions] --> Fetch[fetch_lists]
  Fetch --> Map[Map state]
  Map --> Process[process_list]
  Process --> Notify[notify]
  Fetch --> API[Open Supply Hub API]
  Fetch --> DDB[(DynamoDB)]
  Process --> DDB
  Process --> S3[(S3)]
  Process --> GDrive[Google Drive]
  Notify --> Slack[Slack]
  Notify --> Monday[Monday]
```

### State Management

Each processed facility list is recorded in DynamoDB (keyed by list ID). The `fetch_lists` task reads this table to determine which lists still need processing; `process_list` updates it after a list is handled successfully.

## Process

| Step | Description                                                                                                          |
| ---- | -------------------------------------------------------------------------------------------------------------------- |
| 1    | Fetch newly processed lists and queue them for processing. Lists are retrieved via `GET /api/admin-facility-lists/`. |
| 2    | For each list, download the file from S3, run facility list validation, and upload the report to Google Drive.       |
| 3    | Send notifications to Slack and Monday so that data moderators can review the report.                                |

## Configuration

### Secrets Manager

Store sensitive values in AWS Secrets Manager and inject them at runtime.

| Variable                   | Description                                                                |
| -------------------------- | -------------------------------------------------------------------------- |
| `OS_HUB_API_TOKEN`         | API token used to authenticate requests to Open Supply Hub.                |
| `MONDAY_API_KEY`           | API token used to post items to the Monday board.                          |
| `SLACK_API_URL`            | Webhook URL used to send Slack notifications.                              |
| `GOOGLE_DRIVE_SERVICE_KEY` | Google service account credentials used to upload reports to Google Drive. |

### Environment Variables

Nonsensitive configuration can be set as plain Lambda environment variables.

| Variable                           | Description                                                       |
| ---------------------------------- | ----------------------------------------------------------------- |
| `OS_HUB_API_URL`                   | Base URL of the Open Supply Hub API.                              |
| `MONDAY_API_URL`                   | Base URL of the Monday.com API.                                   |
| `AWS_STORAGE_BUCKET_NAME`          | S3 bucket where uploaded facility list files are stored.          |
| `GOOGLE_DRIVE_SHARED_DIRECTORY_ID` | Google Drive folder ID where validation reports are uploaded.     |
| `MONDAY_BOARD_ID`                  | ID of the Monday board to post the update.                        |
| `CONTRIBOT_STATE_TABLE_NAME`       | DynamoDB table that stores the state of processed facility lists. |

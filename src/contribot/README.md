# ContriBot Lambda Functions

In this directory you'll find a set of Lambda functions that validate list uploads.

The current process consists of the following three steps:

1. Get newly processed lists and queue them for processing.
2. Go through each list, download the file from S3, run the ContriCleaner report, and upload it to Google Drive.
3. Send notifications to Slack and Monday so that data moderators can look at the report.

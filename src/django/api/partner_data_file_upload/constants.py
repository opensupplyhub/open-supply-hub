import re

from botocore.config import Config

DEVELOPER_PROCESSING_ERROR_PREFIX = "Contact developers: "

BATCH_PARTNER_DATA_FILE_UPLOAD_SETTING_NAMES = (
    "BATCH_PARTNER_DATA_FILE_UPLOAD_JOB_QUEUE_NAME",
    "BATCH_PARTNER_DATA_FILE_UPLOAD_JOB_DEF_NAME",
)

DEVELOPER_ERROR_HINTS = (
    "Google Service Account",
    "AWS credentials",
    *BATCH_PARTNER_DATA_FILE_UPLOAD_SETTING_NAMES,
)

BATCH_CLIENT_CONFIG = Config(
    connect_timeout=5,
    read_timeout=15,
    retries={"max_attempts": 2},
)

BEFORE_SUBMIT_PARTNER_DATA_FILE_MSG = (
    "before submitting a partner data file for processing."
)

BATCH_JOB_QUEUE_ENTRY_UUID_PARAM = "queueentryuuid"

GOOGLE_SERVICE_ACCOUNT_CREDS_ENV_VAR = "GOOGLE_SERVICE_ACCOUNT_CREDS_BASE64"
GOOGLE_SHEETS_SCOPES = ("https://www.googleapis.com/auth/spreadsheets",)
GOOGLE_SHEETS_HTTP_TIMEOUT_SECONDS = 60

# Spreadsheet column letters use base-26 encoding (A-Z).
SPREADSHEET_LETTER_BASE = 26
# New Google Sheets start with columns A through Z.
DEFAULT_SHEET_COLUMN_COUNT = SPREADSHEET_LETTER_BASE

SHEET_TRACKING_COLUMNS = ("error", "moderation_id")

# Stay under Google Sheets write quota (60 requests/min per user).
SHEETS_ROW_PROCESSING_DELAY_SECONDS = 1.1

SNAKE_CASE_COLUMN_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")
RESERVED_COLUMNS = frozenset({"os_id", "error", "moderation_id"})

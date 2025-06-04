import os
import base64
import json
from django.core.management.base import BaseCommand
import logging
from google.oauth2 import service_account
from googleapiclient.discovery import build

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Load data directly into the database from a google sheet."

    def add_arguments(self, parser):
        parser.add_argument(
            "--sheet_id",
            type=str,
            help="The ID of the Google Sheet to load data from.",
            required=True,
        )
        parser.add_argument(
            "--range",
            type=str,
            help="The range of cells to read from the Google Sheet.",
            required=True,
        )
        parser.add_argument(
            "--columns",
            type=str,
            help="Comma-separated list of columns to read from the Google Sheet in particular order.",
            required=True,
        )

    def handle(self, *args, **options):
        columns = []

        for col in options["columns"].split(","):
            columns.append(col.strip())

        if not columns:
            raise ValueError("No columns specified for data loading.")

        sheet_id = options["sheet_id"]

        logger.info(
            f"Starting data load from Google Sheet with ID: {sheet_id}")

        SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

        base64_gdrive_creds = os.getenv("GOOGLE_SERVICE_ACCOUNT_CREDS_BASE64")

        if base64_gdrive_creds is None:
            raise ValueError("Google Service Account credentials not found!")

        decoded_creds = base64.b64decode(base64_gdrive_creds).decode("utf-8")

        credentials = service_account.Credentials.from_service_account_info(
            info=json.loads(decoded_creds),
            scopes=SCOPES,
        )
        logger.info("Initialized Google service account credentials")

        service = build(
            "sheets",
            "v4",
            credentials=credentials,
        )
        logger.info("Built Google Sheets service")

        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range=options["range"],  # Adjust the range as needed
        ).execute()

        logger.info(
            f"Fetched data from Google Sheet with ID: '{sheet_id}' and range: '{options['range']}'"
        )

        rows = result.get("values", [])

        if not rows:
            raise ValueError(
                "No data found in the spreadsheet. Please check the range and sheet ID."
            )

        logger.info(f"Data fetched successfully: '{len(rows)}' rows")

        for idx, row in enumerate(rows):
            logger.info(f"Processing row: '{idx + 1}'")
            record = {}

            for col_idx, column in enumerate(columns):
                record[column] = None

                if col_idx < len(row):
                    record[column] = row[col_idx]

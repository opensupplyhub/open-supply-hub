import base64
import json
import os
import re
import string
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import google_auth_httplib2
import httplib2
from google.oauth2 import service_account
from googleapiclient.discovery import build

from api.partner_data_file_upload.constants import (
    DEFAULT_SHEET_COLUMN_COUNT,
    GOOGLE_SERVICE_ACCOUNT_CREDS_ENV_VAR,
    GOOGLE_SHEETS_HTTP_TIMEOUT_SECONDS,
    GOOGLE_SHEETS_SCOPES,
    SHEET_TRACKING_COLUMNS,
    SPREADSHEET_LETTER_BASE,
)
from api.partner_data_file_upload.parsing.types import header_label


@dataclass
class SheetWorkbook:
    spreadsheet_id: str
    sheet_name: str
    tab_id: int
    column_count: int
    headers: List[str]
    rows: List[List[str]]


class GoogleSheetClient:
    def __init__(self, service):
        self.service = service

    @classmethod
    def from_env(cls) -> "GoogleSheetClient":
        scopes = list(GOOGLE_SHEETS_SCOPES)
        base64_creds = os.getenv(GOOGLE_SERVICE_ACCOUNT_CREDS_ENV_VAR)
        if base64_creds is None:
            raise ValueError("Google Service Account credentials not found!")

        decoded = base64.b64decode(base64_creds).decode("utf-8")
        credentials = service_account.Credentials.from_service_account_info(
            info=json.loads(decoded),
            scopes=scopes,
        )
        http = httplib2.Http(timeout=GOOGLE_SHEETS_HTTP_TIMEOUT_SECONDS)
        authorized_http = google_auth_httplib2.AuthorizedHttp(
            credentials,
            http=http,
        )
        return cls(build("sheets", "v4", http=authorized_http))

    @staticmethod
    def parse_spreadsheet_id(link: str) -> str:
        patterns = [
            r"/spreadsheets/d/([a-zA-Z0-9_-]+)",
            r"[?&]id=([a-zA-Z0-9_-]+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, link)
            if match:
                return match.group(1)
        raise ValueError(f"Could not parse Google Sheet id from link: {link}")

    @staticmethod
    def parse_tab_gid(link: str) -> Optional[int]:
        match = re.search(r"[?&]gid=(\d+)", link)
        return int(match.group(1)) if match else None

    def load_workbook(self, link: str) -> SheetWorkbook:
        spreadsheet_id = self.parse_spreadsheet_id(link)
        tab_gid = self.parse_tab_gid(link)
        metadata = self.service.spreadsheets().get(
            spreadsheetId=spreadsheet_id
        ).execute()
        sheet_name, tab_id, column_count = self._resolve_sheet(
            metadata,
            tab_gid,
        )
        end_column = self._column_letter(column_count - 1)
        values = self.service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=f"{sheet_name}!A:{end_column}",
        ).execute().get("values", [])
        if not values:
            raise ValueError("Google Sheet is empty")

        return SheetWorkbook(
            spreadsheet_id=spreadsheet_id,
            sheet_name=sheet_name,
            tab_id=tab_id,
            column_count=column_count,
            headers=values[0],
            rows=values[1:],
        )

    def ensure_tracking_columns(
        self,
        workbook: SheetWorkbook,
    ) -> Dict[str, int]:
        column_labels = [
            header_label(header)
            for header in workbook.headers
        ]
        column_indexes = {}
        next_column_index = len(workbook.headers)

        for tracking_column in SHEET_TRACKING_COLUMNS:
            if tracking_column in column_labels:
                column_indexes[tracking_column] = column_labels.index(
                    tracking_column
                )
                continue

            column_indexes[tracking_column] = next_column_index
            next_column_index += 1

        required_column_count = max(
            workbook.column_count,
            max(column_indexes.values()) + 1,
        )
        self._ensure_grid_column_count(workbook, required_column_count)

        for tracking_column in SHEET_TRACKING_COLUMNS:
            if tracking_column in column_labels:
                continue

            column_index = column_indexes[tracking_column]
            column_letter = self._column_letter(column_index)
            self.service.spreadsheets().values().update(
                spreadsheetId=workbook.spreadsheet_id,
                range=f"{workbook.sheet_name}!{column_letter}1",
                valueInputOption="RAW",
                body={"values": [[tracking_column]]},
            ).execute()

        return column_indexes

    def _ensure_grid_column_count(
        self,
        workbook: SheetWorkbook,
        required_column_count: int,
    ) -> None:
        if required_column_count <= workbook.column_count:
            return

        self.service.spreadsheets().batchUpdate(
            spreadsheetId=workbook.spreadsheet_id,
            body={
                "requests": [
                    {
                        "updateSheetProperties": {
                            "properties": {
                                "sheetId": workbook.tab_id,
                                "gridProperties": {
                                    "columnCount": required_column_count,
                                },
                            },
                            "fields": "gridProperties.columnCount",
                        },
                    },
                ],
            },
        ).execute()
        workbook.column_count = required_column_count

    def mark_row(
        self,
        workbook: SheetWorkbook,
        row_index: int,
        cols_count: int,
        error_col: int,
        moderation_id_col: int,
        error_message: str,
        moderation_id: str,
    ) -> None:
        has_error = bool(error_message)
        bg_color = (
            {"red": 1.0, "green": 0.8, "blue": 0.8}
            if has_error
            else None
        )
        requests = [
            {
                "repeatCell": {
                    "range": {
                        "sheetId": workbook.tab_id,
                        "startRowIndex": row_index - 1,
                        "endRowIndex": row_index,
                        "startColumnIndex": 0,
                        "endColumnIndex": cols_count,
                    },
                    "cell": {
                        "userEnteredFormat": {"backgroundColor": bg_color}
                    },
                    "fields": "userEnteredFormat.backgroundColor",
                }
            },
            {
                "updateCells": {
                    "rows": [{"values": [{"userEnteredValue": {
                        "stringValue": error_message
                    }}]}],
                    "fields": "userEnteredValue",
                    "start": {
                        "sheetId": workbook.tab_id,
                        "rowIndex": row_index - 1,
                        "columnIndex": error_col,
                    },
                }
            },
            {
                "updateCells": {
                    "rows": [{"values": [{"userEnteredValue": {
                        "stringValue": moderation_id
                    }}]}],
                    "fields": "userEnteredValue",
                    "start": {
                        "sheetId": workbook.tab_id,
                        "rowIndex": row_index - 1,
                        "columnIndex": moderation_id_col,
                    },
                }
            },
        ]
        self.service.spreadsheets().batchUpdate(
            spreadsheetId=workbook.spreadsheet_id,
            body={"requests": requests},
        ).execute()

    @staticmethod
    def _resolve_sheet(metadata, tab_gid) -> Tuple[str, int, int]:
        sheets = metadata.get("sheets", [])
        if not sheets:
            raise ValueError("Spreadsheet does not contain any sheets")

        if tab_gid is not None:
            for sheet in sheets:
                props = sheet.get("properties", {})
                if props.get("sheetId") == tab_gid:
                    return GoogleSheetClient._sheet_properties(props)
            raise ValueError(f"Could not find a tab with gid={tab_gid}")

        return GoogleSheetClient._sheet_properties(sheets[0]["properties"])

    @staticmethod
    def _sheet_properties(props) -> Tuple[str, int, int]:
        column_count = props.get("gridProperties", {}).get(
            "columnCount",
            DEFAULT_SHEET_COLUMN_COUNT,
        )
        return props["title"], props["sheetId"], column_count

    @staticmethod
    def _column_letter(column_index: int) -> str:
        if column_index < 0:
            raise ValueError("Column index must be non-negative.")

        column_number = column_index + 1
        letters = []
        while column_number > 0:
            column_number, remainder = divmod(
                column_number - 1,
                SPREADSHEET_LETTER_BASE,
            )
            letters.append(string.ascii_uppercase[remainder])
        return "".join(reversed(letters))

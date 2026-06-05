import base64
import json
import os
import re
import string
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from google.oauth2 import service_account
from googleapiclient.discovery import build

from api.partner_data_file_upload.parsing.types import header_label


@dataclass
class SheetWorkbook:
    spreadsheet_id: str
    sheet_name: str
    tab_id: int
    headers: List[str]
    rows: List[List[str]]


class GoogleSheetClient:
    TRACKING_COLUMNS = ("error", "moderation_id")

    def __init__(self, service):
        self.service = service

    @classmethod
    def from_env(cls) -> "GoogleSheetClient":
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        base64_creds = os.getenv("GOOGLE_SERVICE_ACCOUNT_CREDS_BASE64")
        if base64_creds is None:
            raise ValueError("Google Service Account credentials not found!")

        decoded = base64.b64decode(base64_creds).decode("utf-8")
        credentials = service_account.Credentials.from_service_account_info(
            info=json.loads(decoded),
            scopes=scopes,
        )
        return cls(build("sheets", "v4", credentials=credentials))

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
        sheet_name, tab_id = self._resolve_sheet(metadata, tab_gid)
        values = self.service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=f"{sheet_name}!A:Z",
        ).execute().get("values", [])
        if not values:
            raise ValueError("Google Sheet is empty")

        return SheetWorkbook(
            spreadsheet_id=spreadsheet_id,
            sheet_name=sheet_name,
            tab_id=tab_id,
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

        for tracking_column in self.TRACKING_COLUMNS:
            if tracking_column in column_labels:
                column_indexes[tracking_column] = column_labels.index(
                    tracking_column
                )
                continue

            column_letter = self._column_letter(next_column_index)
            self.service.spreadsheets().values().update(
                spreadsheetId=workbook.spreadsheet_id,
                range=f"{workbook.sheet_name}!{column_letter}1",
                valueInputOption="RAW",
                body={"values": [[tracking_column]]},
            ).execute()
            column_indexes[tracking_column] = next_column_index
            next_column_index += 1

        return column_indexes

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
    def _resolve_sheet(metadata, tab_gid) -> Tuple[str, int]:
        sheets = metadata.get("sheets", [])
        if not sheets:
            raise ValueError("Spreadsheet does not contain any sheets")

        if tab_gid is not None:
            for sheet in sheets:
                props = sheet.get("properties", {})
                if props.get("sheetId") == tab_gid:
                    return props["title"], props["sheetId"]
            raise ValueError(f"Could not find a tab with gid={tab_gid}")

        props = sheets[0]["properties"]
        return props["title"], props["sheetId"]

    @staticmethod
    def _column_letter(column_index: int) -> str:
        if column_index >= len(string.ascii_uppercase):
            raise ValueError(
                "Too many columns in Google Sheet to append tracking columns."
            )
        return string.ascii_uppercase[column_index]

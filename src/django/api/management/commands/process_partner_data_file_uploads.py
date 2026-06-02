import base64
import json
import logging
import os
import re
import string
from dataclasses import dataclass
from typing import Dict, List, Mapping, Optional, Tuple

from django.core.management.base import BaseCommand
from django.utils import timezone
from google.oauth2 import service_account
from googleapiclient.discovery import build

from api.models.facility.facility import Facility
from api.models.moderation_event import ModerationEvent
from api.models.partner_data_file_upload import PartnerDataFileUpload
from api.models.partner_field import PartnerField
from api.moderation_event_actions.creation.dtos.create_moderation_event_dto import (  # noqa: E501
    CreateModerationEventDTO,
)
from api.moderation_event_actions.creation.location_contribution.location_contribution import (  # noqa: E501
    LocationContribution,
)
from api.moderation_event_actions.creation.moderation_event_creator import (
    ModerationEventCreator,
)

logger = logging.getLogger(__name__)


@dataclass
class SheetWorkbook:
    spreadsheet_id: str
    sheet_name: str
    tab_id: int
    headers: List[str]
    rows: List[List[str]]


@dataclass
class SheetProcessingContext:
    workbook: SheetWorkbook
    selected_columns: List[str]
    selected_header_map: Dict[str, int]
    partner_fields_by_name: Dict[str, PartnerField]
    tracking_columns: Dict[str, int]
    cols_count: int


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
        normalized = [
            PartnerFieldSheetParser.normalize_header(header)
            for header in workbook.headers
        ]
        column_indexes = {}
        next_column_index = len(workbook.headers)

        for tracking_column in self.TRACKING_COLUMNS:
            if tracking_column in normalized:
                column_indexes[tracking_column] = normalized.index(
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


class PartnerFieldSheetParser:
    REQUIRED_COLUMNS = ("os_id",)

    @staticmethod
    def normalize_header(header) -> str:
        if header is None:
            return ""
        return str(header).strip().lower().replace(" ", "_")

    @classmethod
    def parse_columns_to_process(cls, raw_columns: str) -> List[str]:
        columns = [
            cls.normalize_header(column)
            for column in str(raw_columns).split(",")
            if cls.normalize_header(column)
        ]
        if not columns:
            raise ValueError("columns_to_process cannot be empty")
        return columns

    @classmethod
    def build_header_map(cls, headers: List[str]) -> Dict[str, int]:
        return {
            cls.normalize_header(header): idx
            for idx, header in enumerate(headers)
            if cls.normalize_header(header)
        }

    @classmethod
    def validate_preflight(
        cls,
        selected_columns: List[str],
        contributor,
    ) -> Dict[str, PartnerField]:
        for required in cls.REQUIRED_COLUMNS:
            if required not in selected_columns:
                raise ValueError(
                    "columns_to_process must include required "
                    f"column '{required}'"
                )

        partner_column_names = [
            column for column in selected_columns if column != "os_id"
        ]
        if not partner_column_names:
            raise ValueError(
                "columns_to_process must include at least one partner field "
                "column in addition to os_id."
            )

        partner_fields = PartnerField.objects.filter(
            name__in=partner_column_names,
            active=True,
        )
        partner_fields_by_name = {
            field.name: field for field in partner_fields
        }

        unknown_columns = sorted(
            set(partner_column_names) - set(partner_fields_by_name.keys())
        )
        if unknown_columns:
            raise ValueError(
                "Unknown or inactive partner field columns: "
                f"{','.join(unknown_columns)}"
            )

        contributor_allowed = set(
            contributor.partner_fields.values_list("name", flat=True)
        )
        unauthorized = sorted(
            set(partner_column_names) - contributor_allowed
        )
        if unauthorized:
            raise ValueError(
                "Contributor is not permitted to write partner fields: "
                f"{','.join(unauthorized)}"
            )

        return partner_fields_by_name

    @staticmethod
    def build_record_from_row(
        row: List[str],
        header_map: Mapping[str, int],
    ) -> Dict[str, object]:
        record = {}
        for field_name, col_idx in header_map.items():
            value = row[col_idx] if col_idx < len(row) else None
            record[field_name] = (
                value.strip() if isinstance(value, str) else value
            )
        return record

    @staticmethod
    def row_has_values(record: Mapping[str, object]) -> bool:
        return any(
            value is not None and (not isinstance(value, str) or value.strip())
            for value in record.values()
        )

    @staticmethod
    def is_cell_empty(value: object) -> bool:
        if value is None:
            return True
        if isinstance(value, str) and not value.strip():
            return True
        return False

    @classmethod
    def parse_cell_value(cls, value: object, partner_field: PartnerField):
        if partner_field.type == PartnerField.STRING:
            return str(value).strip()

        if partner_field.type == PartnerField.INT:
            if isinstance(value, bool):
                raise ValueError("Expected an integer, not a boolean.")
            if isinstance(value, int):
                return value
            if isinstance(value, float) and value.is_integer():
                return int(value)
            try:
                return int(str(value).strip())
            except (TypeError, ValueError) as error:
                raise ValueError(
                    f"Expected an integer, not '{value}'."
                ) from error

        if partner_field.type == PartnerField.FLOAT:
            if isinstance(value, bool):
                raise ValueError("Expected a number, not a boolean.")
            if isinstance(value, (int, float)):
                return float(value)
            try:
                return float(str(value).strip())
            except (TypeError, ValueError) as error:
                raise ValueError(
                    f"Expected a number, not '{value}'."
                ) from error

        if partner_field.type == PartnerField.OBJECT:
            if isinstance(value, (dict, list)):
                return value
            raw_value = str(value).strip()
            try:
                return json.loads(raw_value)
            except json.JSONDecodeError as error:
                raise ValueError(f"Invalid JSON: {error.msg}") from error

        raise ValueError(
            f"Unsupported partner field type '{partner_field.type}'."
        )

    @classmethod
    def build_patch_raw_data(
        cls,
        record: Mapping[str, object],
        partner_fields_by_name: Mapping[str, PartnerField],
    ) -> Dict[str, object]:
        raw_data = {}

        for column_name, cell_value in record.items():
            if column_name == "os_id":
                continue
            if cls.is_cell_empty(cell_value):
                continue

            partner_field = partner_fields_by_name[column_name]
            try:
                raw_data[column_name] = cls.parse_cell_value(
                    cell_value,
                    partner_field,
                )
            except ValueError as error:
                raise ValueError(f"{column_name}: {error}") from error

        if not raw_data:
            raise ValueError("No partner field values provided.")

        return raw_data


class PartnerPatchModerationEventCreator:
    def __init__(self, me_creator: ModerationEventCreator):
        self.me_creator = me_creator

    def create(
        self,
        contributor,
        record: Mapping[str, object],
        partner_fields_by_name: Mapping[str, PartnerField],
    ) -> str:
        os_id = str(record.get("os_id") or "").strip()
        if not os_id:
            raise ValueError("Missing required value for 'os_id'")

        try:
            facility = Facility.objects.get(id=os_id)
        except Facility.DoesNotExist as error:
            raise ValueError(
                f"Facility with os_id '{os_id}' was not found"
            ) from error

        raw_data = PartnerFieldSheetParser.build_patch_raw_data(
            record,
            partner_fields_by_name,
        )
        event_dto = CreateModerationEventDTO(
            contributor=contributor,
            raw_data=raw_data,
            request_type=ModerationEvent.RequestType.UPDATE.value,
            os=facility,
        )
        result = self.me_creator.perform_event_creation(event_dto)
        if result.errors:
            raise ValueError(self.format_api_errors(result.errors))

        return str(result.moderation_event.uuid)

    @staticmethod
    def format_api_errors(errors: Mapping[str, object]) -> str:
        if not errors:
            return "Unknown error."

        messages = []
        detail = errors.get("detail")
        if isinstance(detail, str) and detail:
            messages.append(detail)

        error_items = errors.get("errors", [])
        if isinstance(error_items, list):
            for item in error_items:
                if isinstance(item, dict):
                    field = item.get("field", "")
                    item_detail = item.get("detail", "")
                    if field and item_detail:
                        messages.append(f"{field}: {item_detail}")
                    elif item_detail:
                        messages.append(str(item_detail))
                    elif field:
                        messages.append(str(field))
                elif item:
                    messages.append(str(item))

        if messages:
            return "; ".join(messages)

        return json.dumps(errors)


class PartnerDataFileUploadProcessor:
    def __init__(
        self,
        sheets_client: GoogleSheetClient,
        me_creator: Optional[ModerationEventCreator] = None,
    ):
        self.sheets_client = sheets_client
        self.event_creator = PartnerPatchModerationEventCreator(
            me_creator or ModerationEventCreator(LocationContribution())
        )

    def process(self, queue_row: PartnerDataFileUpload) -> None:
        try:
            context = self._build_context(queue_row)
            self._process_rows(queue_row, context)
            self._mark_queue_row_processed(queue_row)
        except Exception as error:
            queue_row.processing_error = str(error)
            queue_row.save(update_fields=["processing_error", "updated_at"])
            logger.exception(
                "Failed processing partner data file row uuid=%s",
                queue_row.uuid,
            )

    def _build_context(
        self,
        queue_row: PartnerDataFileUpload,
    ) -> SheetProcessingContext:
        workbook = self.sheets_client.load_workbook(
            queue_row.google_drive_file_link
        )
        header_map = PartnerFieldSheetParser.build_header_map(workbook.headers)
        selected_columns = PartnerFieldSheetParser.parse_columns_to_process(
            queue_row.columns_to_process
        )
        partner_fields_by_name = PartnerFieldSheetParser.validate_preflight(
            selected_columns,
            queue_row.contributor,
        )

        missing_selected_columns = [
            column
            for column in selected_columns
            if column not in header_map
        ]
        if missing_selected_columns:
            raise ValueError(
                "Selected columns were not found in the sheet header: "
                f"{','.join(missing_selected_columns)}"
            )

        selected_header_map = {
            column: header_map[column]
            for column in selected_columns
        }
        tracking_columns = self.sheets_client.ensure_tracking_columns(
            workbook
        )
        cols_count = max(
            len(workbook.headers),
            tracking_columns["error"] + 1,
            tracking_columns["moderation_id"] + 1,
        )

        return SheetProcessingContext(
            workbook=workbook,
            selected_columns=selected_columns,
            selected_header_map=selected_header_map,
            partner_fields_by_name=partner_fields_by_name,
            tracking_columns=tracking_columns,
            cols_count=cols_count,
        )

    def _process_rows(
        self,
        queue_row: PartnerDataFileUpload,
        context: SheetProcessingContext,
    ) -> None:
        error_col = context.tracking_columns["error"]
        moderation_id_col = context.tracking_columns["moderation_id"]

        for row_idx, row_values in enumerate(context.workbook.rows, start=2):
            record = PartnerFieldSheetParser.build_record_from_row(
                row_values,
                context.selected_header_map,
            )
            if not PartnerFieldSheetParser.row_has_values(record):
                continue

            try:
                moderation_id = self.event_creator.create(
                    queue_row.contributor,
                    record,
                    context.partner_fields_by_name,
                )
                self.sheets_client.mark_row(
                    context.workbook,
                    row_idx,
                    context.cols_count,
                    error_col,
                    moderation_id_col,
                    "",
                    moderation_id,
                )
            except Exception as error:
                self.sheets_client.mark_row(
                    context.workbook,
                    row_idx,
                    context.cols_count,
                    error_col,
                    moderation_id_col,
                    str(error),
                    "",
                )
                logger.error(
                    "Error creating moderation event for row %s: %s",
                    row_idx,
                    str(error),
                )

    @staticmethod
    def _mark_queue_row_processed(queue_row: PartnerDataFileUpload) -> None:
        queue_row.is_processed = True
        queue_row.processed_at = timezone.now()
        queue_row.processing_error = ""
        queue_row.save(
            update_fields=[
                "is_processed",
                "processed_at",
                "processing_error",
                "updated_at",
            ]
        )


class Command(BaseCommand):
    help = (
        "Process queued partner Google Sheets and create pending moderation "
        "events for partner-field production location updates."
    )

    def add_arguments(self, parser):
        parser.add_argument("--queue_entry_uuid", type=str, required=False)

    def handle(self, *args, **options):
        rows = (
            PartnerDataFileUpload.objects
            .select_related("contributor")
            .filter(is_processed=False)
        )
        if options.get("queue_entry_uuid"):
            rows = rows.filter(uuid=options["queue_entry_uuid"])

        if not rows.exists():
            logger.info("No unprocessed partner data files found.")
            return

        processor = PartnerDataFileUploadProcessor(
            GoogleSheetClient.from_env()
        )
        for queue_row in rows:
            processor.process(queue_row)

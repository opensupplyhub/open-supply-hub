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
SNAKE_CASE_COLUMN_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")
RESERVED_COLUMNS = frozenset({"os_id", "error", "moderation_id"})


@dataclass
class ColumnMapping:
    column_name: str
    partner_field: PartnerField
    path_segments: Optional[List[str]] = None
    leaf_schema: Optional[dict] = None


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
    data_columns: List[str]
    header_map: Dict[str, int]
    column_mappings: Dict[str, ColumnMapping]
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
        column_labels = [
            PartnerFieldSheetParser.header_label(header)
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


class PartnerFieldSheetParser:
    @staticmethod
    def _raise_validation_errors(errors: List[str]) -> None:
        if errors:
            raise ValueError("; ".join(errors))

    @staticmethod
    def header_label(header) -> str:
        if header is None:
            return ""
        return str(header)

    @classmethod
    def build_header_map(cls, headers: List[str]) -> Dict[str, int]:
        header_map = {}
        duplicate_headers = []
        for idx, header in enumerate(headers):
            column_name = cls.header_label(header)
            if not column_name.strip():
                continue
            if column_name in header_map:
                if column_name not in duplicate_headers:
                    duplicate_headers.append(column_name)
                continue
            header_map[column_name] = idx

        if duplicate_headers:
            raise ValueError(
                "Sheet contains duplicate headers: "
                f"{','.join(sorted(duplicate_headers))}"
            )
        return header_map

    @classmethod
    def validate_headers(cls, header_map: Dict[str, int]) -> List[str]:
        errors = []
        if not header_map:
            errors.append("Google Sheet header row is empty.")
            cls._raise_validation_errors(errors)

        invalid_headers = sorted(
            column
            for column in header_map
            if not SNAKE_CASE_COLUMN_PATTERN.match(column)
        )
        if invalid_headers:
            errors.append(
                "Sheet headers must already be lowercase snake_case "
                "(for example 'os_id', not 'OS ID'): "
                f"{','.join(invalid_headers)}"
            )

        if "os_id" not in header_map:
            errors.append("Sheet must include required column 'os_id'.")

        data_columns = [
            column
            for column in header_map
            if column not in RESERVED_COLUMNS
        ]
        if not data_columns:
            errors.append(
                "Sheet must include at least one partner field column "
                "in addition to os_id."
            )

        cls._raise_validation_errors(errors)
        return data_columns

    @staticmethod
    def parse_json_schema(partner_field: PartnerField) -> Optional[dict]:
        json_schema = partner_field.json_schema
        if json_schema is None:
            return None
        if isinstance(json_schema, dict):
            return json_schema
        if isinstance(json_schema, str):
            try:
                return json.loads(json_schema)
            except (json.JSONDecodeError, TypeError):
                return None
        return None

    @classmethod
    def collect_unsupported_array_paths(
        cls,
        schema: dict,
        prefix_segments: Optional[List[str]] = None,
    ) -> List[str]:
        prefix_segments = prefix_segments or []
        properties = schema.get("properties", {})
        if not isinstance(properties, dict):
            return []

        unsupported = []
        for key, subschema in properties.items():
            if not isinstance(subschema, dict):
                continue

            segments = prefix_segments + [key]
            path_str = "_".join(segments)
            if subschema.get("type") == "array":
                unsupported.append(path_str)
                continue

            if cls._is_nested_object_schema(subschema):
                unsupported.extend(
                    cls.collect_unsupported_array_paths(subschema, segments)
                )
        return unsupported

    @classmethod
    def iter_schema_leaf_paths(
        cls,
        schema: dict,
        prefix_segments: Optional[List[str]] = None,
    ):
        prefix_segments = prefix_segments or []
        properties = schema.get("properties", {})
        if not isinstance(properties, dict):
            return

        for key, subschema in properties.items():
            if not isinstance(subschema, dict):
                continue

            segments = prefix_segments + [key]
            schema_type = subschema.get("type")

            if schema_type == "array":
                continue

            if cls._is_nested_object_schema(subschema):
                yield from cls.iter_schema_leaf_paths(subschema, segments)
            else:
                path_str = "_".join(segments)
                yield path_str, segments, subschema

    @staticmethod
    def _is_nested_object_schema(schema: dict) -> bool:
        if schema.get("type") == "object":
            return bool(schema.get("properties"))
        return bool(schema.get("properties")) and schema.get("type") is None

    @classmethod
    def allowed_flattened_columns(
        cls,
        field_name: str,
        schema: dict,
    ) -> Dict[str, Tuple[List[str], dict]]:
        allowed = {}
        for path_str, segments, leaf_schema in cls.iter_schema_leaf_paths(
            schema
        ):
            allowed[f"{field_name}_{path_str}"] = (segments, leaf_schema)
        return allowed

    @classmethod
    def get_contributor_partner_fields(cls, contributor) -> List[PartnerField]:
        return list(
            contributor.partner_fields.order_by("-name")
        )

    @classmethod
    def match_column(
        cls,
        column: str,
        contributor_fields: List[PartnerField],
    ) -> Optional[ColumnMapping]:
        for partner_field in contributor_fields:
            if partner_field.type in (
                PartnerField.STRING,
                PartnerField.INT,
                PartnerField.FLOAT,
            ):
                if column == partner_field.name:
                    return ColumnMapping(
                        column_name=column,
                        partner_field=partner_field,
                    )
                continue

            if partner_field.type != PartnerField.OBJECT:
                continue

            schema = cls.parse_json_schema(partner_field)
            if not schema:
                continue

            prefix = f"{partner_field.name}_"
            if not column.startswith(prefix):
                continue

            allowed = cls.allowed_flattened_columns(
                partner_field.name,
                schema,
            )
            if column not in allowed:
                continue

            path_segments, leaf_schema = allowed[column]
            return ColumnMapping(
                column_name=column,
                partner_field=partner_field,
                path_segments=path_segments,
                leaf_schema=leaf_schema,
            )

        return None

    @classmethod
    def build_column_mappings(
        cls,
        data_columns: List[str],
        contributor,
    ) -> Tuple[Dict[str, ColumnMapping], Dict[str, PartnerField]]:
        contributor_fields = cls.get_contributor_partner_fields(contributor)
        contributor_allowed = {field.name for field in contributor_fields}

        column_mappings = {}
        partner_fields_by_name = {}
        unmatched_columns = []
        unauthorized_fields = set()

        for column in data_columns:
            mapping = cls.match_column(column, contributor_fields)
            if mapping is None:
                unmatched_columns.append(column)
                continue

            if mapping.partner_field.name not in contributor_allowed:
                unauthorized_fields.add(mapping.partner_field.name)
                continue

            column_mappings[column] = mapping
            partner_fields_by_name[mapping.partner_field.name] = (
                mapping.partner_field
            )

        mapping_errors = []
        if unmatched_columns:
            mapping_errors.append(
                "Unknown or invalid sheet columns: "
                f"{','.join(sorted(unmatched_columns))}"
            )

        if unauthorized_fields:
            mapping_errors.append(
                "Contributor is not permitted to write partner field(s): "
                f"{','.join(sorted(unauthorized_fields))}"
            )

        object_fields_without_schema = sorted(
            field.name
            for field in contributor_fields
            if field.type == PartnerField.OBJECT
            and not cls.parse_json_schema(field)
        )
        schema_missing_fields = set()
        for column in data_columns:
            for field_name in object_fields_without_schema:
                if column.startswith(f"{field_name}_"):
                    schema_missing_fields.add(field_name)
        if schema_missing_fields:
            mapping_errors.append(
                "Partner field(s) are object type but have no JSON schema "
                "for flattened columns: "
                f"{','.join(sorted(schema_missing_fields))}"
            )

        for partner_field in contributor_fields:
            if partner_field.type != PartnerField.OBJECT:
                continue

            schema = cls.parse_json_schema(partner_field)
            if not schema:
                continue

            array_paths = cls.collect_unsupported_array_paths(schema)
            if array_paths:
                mapping_errors.append(
                    "Partner field "
                    f"'{partner_field.name}' has unsupported array "
                    "properties: "
                    f"{','.join(sorted(array_paths))}"
                )

        cls._raise_validation_errors(mapping_errors)
        return column_mappings, partner_fields_by_name

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

        raise ValueError(
            f"Unsupported partner field type '{partner_field.type}'."
        )

    @classmethod
    def parse_leaf_cell_value(cls, value: object, leaf_schema: dict):
        schema_type = leaf_schema.get("type")

        if schema_type == "integer":
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

        if schema_type == "number":
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

        if schema_type == "boolean":
            if isinstance(value, bool):
                return value
            normalized = str(value).strip().lower()
            if normalized in ("true", "1", "yes"):
                return True
            if normalized in ("false", "0", "no"):
                return False
            raise ValueError(f"Expected a boolean, not '{value}'.")

        if schema_type == "string" or "enum" in leaf_schema:
            return str(value).strip()

        raise ValueError(
            f"Unsupported JSON schema type '{schema_type}'."
        )

    @staticmethod
    def set_nested_value(
        target: dict,
        path_segments: List[str],
        value: object,
    ) -> None:
        current = target
        for segment in path_segments[:-1]:
            current = current.setdefault(segment, {})
        current[path_segments[-1]] = value

    @classmethod
    def build_patch_raw_data(
        cls,
        record: Mapping[str, object],
        column_mappings: Mapping[str, ColumnMapping],
    ) -> Dict[str, object]:
        raw_data = {}
        object_values = {}
        parse_errors = []

        for column_name, mapping in column_mappings.items():
            cell_value = record.get(column_name)
            if cls.is_cell_empty(cell_value):
                continue

            partner_field = mapping.partner_field
            try:
                if mapping.path_segments is None:
                    raw_data[partner_field.name] = cls.parse_cell_value(
                        cell_value,
                        partner_field,
                    )
                else:
                    nested = object_values.setdefault(partner_field.name, {})
                    parsed_value = cls.parse_leaf_cell_value(
                        cell_value,
                        mapping.leaf_schema,
                    )
                    cls.set_nested_value(
                        nested,
                        mapping.path_segments,
                        parsed_value,
                    )
            except ValueError as error:
                parse_errors.append(f"{column_name}: {error}")

        for field_name, nested_value in object_values.items():
            raw_data[field_name] = nested_value

        if parse_errors:
            cls._raise_validation_errors(parse_errors)

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
        column_mappings: Mapping[str, ColumnMapping],
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
            column_mappings,
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

    def process(self, queue_row: PartnerDataFileUpload) -> bool:
        logger.info(
            "Starting partner data file upload processing for uuid=%s "
            "contributor_id=%s",
            queue_row.uuid,
            queue_row.contributor_id,
        )
        try:
            context = self._build_context(queue_row)
            row_stats = self._process_rows(queue_row, context)
            self._mark_queue_row_processed(queue_row)
            logger.info(
                "Partner data file upload uuid=%s processing completed "
                "successfully. rows_succeeded=%s rows_failed=%s "
                "rows_skipped_empty=%s",
                queue_row.uuid,
                row_stats["rows_succeeded"],
                row_stats["rows_failed"],
                row_stats["rows_skipped_empty"],
            )
            return True
        except Exception as error:
            queue_row.status = PartnerDataFileUpload.Status.FAILED
            queue_row.processing_error = (
                PartnerDataFileUpload.format_upload_processing_error(error)
            )
            queue_row.save(
                update_fields=["status", "processing_error", "updated_at"]
            )
            logger.error(
                "Partner data file upload uuid=%s processing failed: %s",
                queue_row.uuid,
                queue_row.processing_error,
            )
            logger.exception(
                "Failed processing partner data file upload uuid=%s",
                queue_row.uuid,
            )
            return False

    def _build_context(
        self,
        queue_row: PartnerDataFileUpload,
    ) -> SheetProcessingContext:
        workbook = self.sheets_client.load_workbook(
            queue_row.google_drive_file_link
        )
        header_map = PartnerFieldSheetParser.build_header_map(workbook.headers)
        data_columns = PartnerFieldSheetParser.validate_headers(header_map)
        column_mappings, partner_fields_by_name = (
            PartnerFieldSheetParser.build_column_mappings(
                data_columns,
                queue_row.contributor,
            )
        )
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
            data_columns=data_columns,
            header_map=header_map,
            column_mappings=column_mappings,
            partner_fields_by_name=partner_fields_by_name,
            tracking_columns=tracking_columns,
            cols_count=cols_count,
        )

    def _process_rows(
        self,
        queue_row: PartnerDataFileUpload,
        context: SheetProcessingContext,
    ) -> Dict[str, int]:
        error_col = context.tracking_columns["error"]
        moderation_id_col = context.tracking_columns["moderation_id"]
        row_stats = {
            "rows_succeeded": 0,
            "rows_failed": 0,
            "rows_skipped_empty": 0,
        }

        logger.info(
            "Processing sheet rows for upload uuid=%s. data_rows=%s",
            queue_row.uuid,
            len(context.workbook.rows),
        )

        for row_idx, row_values in enumerate(context.workbook.rows, start=2):
            record = PartnerFieldSheetParser.build_record_from_row(
                row_values,
                context.header_map,
            )
            if not PartnerFieldSheetParser.row_has_values(record):
                row_stats["rows_skipped_empty"] += 1
                continue

            try:
                moderation_id = self.event_creator.create(
                    queue_row.contributor,
                    record,
                    context.column_mappings,
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
                row_stats["rows_succeeded"] += 1
                logger.info(
                    "Row %s processed successfully for upload uuid=%s. "
                    "os_id=%s moderation_id=%s",
                    row_idx,
                    queue_row.uuid,
                    record.get("os_id"),
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
                row_stats["rows_failed"] += 1
                logger.error(
                    "Row %s failed for upload uuid=%s. os_id=%s error=%s",
                    row_idx,
                    queue_row.uuid,
                    record.get("os_id"),
                    str(error),
                )

        logger.info(
            "Finished sheet row processing for upload uuid=%s. "
            "rows_succeeded=%s rows_failed=%s rows_skipped_empty=%s",
            queue_row.uuid,
            row_stats["rows_succeeded"],
            row_stats["rows_failed"],
            row_stats["rows_skipped_empty"],
        )
        return row_stats

    @staticmethod
    def _mark_queue_row_processed(queue_row: PartnerDataFileUpload) -> None:
        queue_row.status = PartnerDataFileUpload.Status.PROCESSED
        queue_row.processed_at = timezone.now()
        queue_row.processing_error = ""
        queue_row.save(
            update_fields=[
                "status",
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
        queue_entry_uuid = options.get("queue_entry_uuid")
        logger.info(
            "Starting partner data file upload command."
            + (
                f" queue_entry_uuid={queue_entry_uuid}"
                if queue_entry_uuid
                else ""
            )
        )

        rows = (
            PartnerDataFileUpload.objects
            .select_related("contributor")
            .filter(status=PartnerDataFileUpload.Status.PROCESSING)
        )
        if queue_entry_uuid:
            rows = rows.filter(uuid=queue_entry_uuid)

        if not rows.exists():
            logger.info(
                "No partner data files in PROCESSING status found. "
                "Processing completed."
            )
            return

        upload_count = rows.count()
        logger.info(
            "Found %s partner data file upload(s) in PROCESSING status.",
            upload_count,
        )

        processor = PartnerDataFileUploadProcessor(
            GoogleSheetClient.from_env()
        )
        uploads_succeeded = 0
        uploads_failed = 0
        for queue_row in rows:
            if processor.process(queue_row):
                uploads_succeeded += 1
            else:
                uploads_failed += 1

        logger.info(
            "Partner data file upload command processing completed. "
            "uploads_succeeded=%s uploads_failed=%s uploads_total=%s",
            uploads_succeeded,
            uploads_failed,
            upload_count,
        )

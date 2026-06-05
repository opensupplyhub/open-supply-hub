import json
import re
from typing import Dict, List, Mapping, Optional, Tuple

from api.models.partner_field import PartnerField
from api.partner_data_file_upload.parsing.types import (
    ColumnMapping,
    header_label,
)

SNAKE_CASE_COLUMN_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")
RESERVED_COLUMNS = frozenset({"os_id", "error", "moderation_id"})


class PartnerFieldSheetParser:
    @staticmethod
    def _raise_validation_errors(errors: List[str]) -> None:
        if errors:
            raise ValueError("; ".join(errors))

    @staticmethod
    def header_label(header) -> str:
        return header_label(header)

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
                "Unknown or invalid sheet columns, or columns the "
                "contributor is not authorized to write: "
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

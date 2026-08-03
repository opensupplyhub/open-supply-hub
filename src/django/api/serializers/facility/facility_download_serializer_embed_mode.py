from typing import Dict, List
from api.models.facility.facility_manager_index_new \
    import FacilityIndexNewManager
from api.models.embed_field import EmbedField
from api.models import Contributor
from api.helpers.helpers import get_csv_values, parse_raw_data
from api.models.source import Source
from api.serializers.facility.facility_download_serializer_base import (
    FacilityDownloadSerializerBase,
)


class FacilityDownloadSerializerEmbedMode(FacilityDownloadSerializerBase):
    EMBED_EXTENDED_FIELD_NAMES = {
        "number_of_workers",
        "parent_company",
        "facility_type",
        "processing_type",
        "product_type",
    }

    def __init__(self, *args, **kwargs):
        self.contributor_id = int(kwargs.pop("contributor_id", None))
        self._list_field_indexes_by_header = {}
        super().__init__(*args, **kwargs)
        self.visible_embed_columns = self.get_embed_fields(self.contributor_id)

    def get_headers(self) -> List[str]:
        return [
            *self.COMMON_HEADERS,
            *self.visible_embed_columns,
            self.IS_CLOSED_HEADER,
        ]

    def get_row(self, facility: FacilityIndexNewManager) -> List[str]:
        return [
            *self.get_common_row(facility),
            *self.get_embed_column_values(facility),
            self.get_is_closed(facility),
        ]

    def get_embed_column_values(
        self, facility: FacilityIndexNewManager
    ) -> List[str]:
        """Return visible embed-config columns in the same order as the map."""
        custom_values = self._get_custom_values(facility)
        extended_values = self._get_extended_values(facility)
        return [
            extended_values[column]
            if (
                column in self.EMBED_EXTENDED_FIELD_NAMES
                and str(extended_values.get(column, "")).strip()
            )
            else custom_values.get(column, "") or ""
            for column in self.visible_embed_columns
        ]

    def _get_extended_values(
        self, facility: FacilityIndexNewManager
    ) -> Dict[str, str]:
        """Select and format the owner's top contribution for each field."""
        claimant_contributor_id = (facility.approved_claim or {}).get(
            "contributor_id"
        )
        selected = {}
        ranks = {}
        for field in facility.extended_fields:
            contributor = field.get("contributor") or {}
            if contributor.get("id") != self.contributor_id:
                continue

            field_name = field.get("field_name")
            value = field.get("value") or {}
            if field_name == "facility_type" and not any(
                len(matched) > 2 and matched[2]
                for matched in value.get("matched_values", [])
            ):
                continue

            rank = (
                int(bool(contributor.get("is_verified")))
                + int(bool(field.get("is_verified"))),
                field.get("facility_list_item_id") is None
                or contributor.get("id") == claimant_contributor_id,
                field.get("value_count", 1),
                field.get("created_at") or "",
            )
            if field_name not in ranks or rank > ranks[field_name]:
                selected[field_name] = field
                ranks[field_name] = rank

        return {
            name: self._format_extended_field(field)
            for name, field in selected.items()
        }

    @staticmethod
    def _format_extended_field(field: dict) -> str:
        field_name = field.get("field_name")
        value = field.get("value") or {}

        if field_name == "number_of_workers":
            minimum = value.get("min", 0)
            maximum = value.get("max", 0)
            return (
                str(maximum)
                if minimum == maximum
                else f"{minimum}-{maximum}"
            )

        if field_name == "parent_company":
            return (
                value.get("contributor_name")
                or value.get("name")
                or value.get("raw_value")
                or ""
            )

        if field_name == "facility_type":
            return FacilityDownloadSerializerEmbedMode._join_unique(
                str(matched_value[2])
                for matched_value in value.get("matched_values", [])
                if len(matched_value) > 2 and matched_value[2]
            )

        if field_name == "processing_type":
            raw_values = value.get("raw_values", [])
            if not isinstance(raw_values, list):
                raw_values = str(raw_values).split("|")
            formatted_values = []
            for index, matched_value in enumerate(
                value.get("matched_values", [])
            ):
                matched = (
                    matched_value[3]
                    if len(matched_value) > 3
                    else None
                )
                raw = raw_values[index] if index < len(raw_values) else ""
                formatted_values.append(str(matched or raw))
            return FacilityDownloadSerializerEmbedMode._join_unique(
                filter(None, formatted_values)
            )

        if field_name == "product_type":
            raw_values = value.get("raw_values", [])
            if not isinstance(raw_values, list):
                raw_values = str(raw_values).split("|")
            return FacilityDownloadSerializerEmbedMode._join_unique(
                map(str, raw_values)
            )

        return ""

    @staticmethod
    def _join_unique(values) -> str:
        return "|".join(dict.fromkeys(values))

    def _get_custom_values(
        self, facility: FacilityIndexNewManager
    ) -> Dict[str, str]:
        info = next(
            (
                item
                for item in facility.custom_field_info
                if str(item["contributor_id"]) == str(self.contributor_id)
            ),
            None,
        )
        if info is None:
            return {}

        if info["source_type"] == Source.LIST:
            data_values = get_csv_values(info["raw_data"])
            field_indexes = self._get_list_field_indexes(
                info["list_header"]
            )
            return {
                field: (
                    data_values[index]
                    if (index := field_indexes.get(field)) is not None
                    and index < len(data_values)
                    else ""
                )
                for field in self.visible_embed_columns
            }

        raw_json = parse_raw_data(info["raw_data"])
        return {
            field: raw_json.get(field, "")
            for field in self.visible_embed_columns
        }

    @staticmethod
    def get_embed_fields(contributor_id: int) -> List[str]:
        contributor = Contributor.objects.get(id=contributor_id)
        if contributor.embed_config_id is None:
            return []

        return [
            column_name
            for column_name in EmbedField.objects.filter(
                embed_config_id=contributor.embed_config_id,
                visible=True,
            ).order_by("order").values_list("column_name", flat=True)
            if column_name
        ]

    def _get_list_field_indexes(self, list_header: str):
        if list_header not in self._list_field_indexes_by_header:
            exact_indexes = {}
            casefold_indexes = {}
            for index, field in enumerate(get_csv_values(list_header)):
                exact_indexes.setdefault(field, index)
                casefold_indexes.setdefault(field.casefold(), index)

            field_indexes = {
                field: exact_indexes.get(
                    field,
                    casefold_indexes.get(field.casefold()),
                )
                for field in self.visible_embed_columns
            }
            self._list_field_indexes_by_header[list_header] = field_indexes

        return self._list_field_indexes_by_header[list_header]

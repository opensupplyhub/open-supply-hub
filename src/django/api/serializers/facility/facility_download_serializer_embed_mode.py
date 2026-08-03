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
    embed_fields = []
    contributor_id = None
    visible_embed_columns = []
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
        self.embed_fields = [
            field
            for field in self.visible_embed_columns
            if field not in self.EMBED_EXTENDED_FIELD_NAMES
        ]

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
        custom_values = self.get_contributor_field_values_by_name(facility)
        extended_values = self.get_formatted_extended_field_values(facility)

        values = []
        for column in self.visible_embed_columns:
            if column in self.EMBED_EXTENDED_FIELD_NAMES:
                value = extended_values.get(column, "")
                if not str(value).strip():
                    value = custom_values.get(column, "")
            else:
                value = custom_values.get(column, "")
            values.append(value or "")

        return values

    def get_formatted_extended_field_values(
        self, facility: FacilityIndexNewManager,
    ) -> Dict[str, str]:
        return {
            field["field_name"]: self.__format_extended_field(field)
            for field in self.get_displayed_extended_fields(facility)
        }

    def get_displayed_extended_fields(
        self, facility: FacilityIndexNewManager
    ) -> List[dict]:
        """Return the extended-field contributions the embedded map shows.

        The embedded profile drops other contributors' contributions to
        promote only the owner's data, and renders a single value per field
        because ``FacilityDetailsItem`` suppresses additional entries while
        ``embed`` is set. The download mirrors both rules so an embed export
        never contains values that are hidden on the map it came from.
        """
        claimant_contributor_id = (facility.approved_claim or {}).get(
            "contributor_id"
        )
        fields = [
            field
            for field in facility.extended_fields
            if (field.get("contributor") or {}).get("id")
            == self.contributor_id
        ]
        fields_by_name = {}
        for field in fields:
            fields_by_name.setdefault(field.get("field_name"), []).append(
                field
            )

        selected_fields = []
        for grouped_fields in fields_by_name.values():
            displayable_fields = [
                field
                for field in grouped_fields
                if self.__is_extended_field_displayable(field)
            ]
            ranked_fields = sorted(
                displayable_fields,
                key=lambda field: self.__extended_field_sort_order(
                    field,
                    claimant_contributor_id,
                ),
                reverse=True,
            )
            selected_fields.extend(ranked_fields[:1])

        return selected_fields

    @staticmethod
    def __extended_field_sort_order(
        field: dict, claimant_contributor_id: int
    ):
        contributor = field.get("contributor") or {}
        verified_count = int(bool(contributor.get("is_verified")))
        verified_count += int(bool(field.get("is_verified")))
        is_from_claim = (
            field.get("facility_list_item_id") is None
            or contributor.get("id") == claimant_contributor_id
        )
        return (
            verified_count,
            is_from_claim,
            field.get("value_count", 1),
            field.get("created_at") or "",
        )

    @staticmethod
    def __is_extended_field_displayable(field: dict) -> bool:
        if field.get("field_name") != "facility_type":
            return True

        value = field.get("value") or {}
        return any(
            len(matched_value) > 2 and matched_value[2]
            for matched_value in value.get("matched_values", [])
        )

    @staticmethod
    def __format_extended_field(field: dict) -> str:
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
            return FacilityDownloadSerializerEmbedMode.__join_unique(
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
            return FacilityDownloadSerializerEmbedMode.__join_unique(
                filter(None, formatted_values)
            )

        if field_name == "product_type":
            raw_values = value.get("raw_values", [])
            if not isinstance(raw_values, list):
                raw_values = str(raw_values).split("|")
            return FacilityDownloadSerializerEmbedMode.__join_unique(
                map(str, raw_values)
            )

        return ""

    @staticmethod
    def __join_unique(values) -> str:
        return "|".join(dict.fromkeys(values))

    def get_contributor_field_values_by_name(
        self, facility: FacilityIndexNewManager
    ) -> Dict[str, str]:
        infos = [
            info
            for info in facility.custom_field_info
            if str(info["contributor_id"]) == str(self.contributor_id)
        ]
        info = infos[0] if len(infos) > 0 else None
        if info is None:
            return {field: "" for field in self.visible_embed_columns}

        if info["source_type"] == Source.LIST:
            data_values = get_csv_values(info["raw_data"])
            field_indexes = self.__get_list_field_indexes(
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

    def get_contributor_custom_fields(self, facility: FacilityIndexNewManager):
        custom_values = self.get_contributor_field_values_by_name(facility)
        return [custom_values.get(field, "") for field in self.embed_fields]

    @staticmethod
    def get_embed_fields(contributor_id: int) -> List[str]:
        embed_fields = []
        contributor = Contributor.objects.get(id=contributor_id)
        config = contributor.embed_config

        if config and EmbedField.objects.filter(embed_config=config).exists():
            embed_fields = EmbedField.objects.filter(
                embed_config=config, visible=True
            ).order_by("order")

        return [
            field["column_name"]
            for field in embed_fields.values("column_name")
            if field["column_name"]
        ]

    def __get_list_field_indexes(self, list_header: str):
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

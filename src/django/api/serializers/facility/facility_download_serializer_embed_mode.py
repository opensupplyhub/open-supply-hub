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
        """Join all of the embed owner's values for each standard field."""
        owner_fields = [
            field
            for field in facility.extended_fields
            if (field.get("contributor") or {}).get("id")
            == self.contributor_id
        ]
        return dict(
            zip(
                self.EXTENDED_FIELDS_HEADERS,
                self.get_extended_fields(owner_fields),
            )
        )

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

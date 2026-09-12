from typing import List
from api.models.facility.facility_manager_index_new \
    import FacilityIndexNewManager
from api.models.embed_field import EmbedField
from api.models import Contributor
from api.helpers.helpers import (
    get_csv_values,
    parse_raw_data,
    try_parse_int_from_float,
)
from api.models.source import Source
from api.serializers.facility.facility_download_serializer_base import (
    FacilityDownloadSerializerBase,
)


class FacilityDownloadSerializerEmbedMode(FacilityDownloadSerializerBase):
    def __init__(self, *args, **kwargs):
        self.contributor_id = int(kwargs.pop("contributor_id", None))
        self._list_field_indexes_by_header = {}
        super().__init__(*args, **kwargs)
        fields = self.get_embed_fields(self.contributor_id)
        self.embed_fields = [
            field
            for field in fields
            if field not in self.EXTENDED_FIELDS_HEADERS
        ]

    def get_headers(self) -> List[str]:
        return [
            *self.COMMON_HEADERS,
            *self.embed_fields,
            *self.EXTENDED_FIELDS_HEADERS,
            self.IS_CLOSED_HEADER,
        ]

    def get_row(self, facility: FacilityIndexNewManager) -> List[str]:
        return [
            *self.get_common_row(facility),
            *self.get_contributor_custom_fields(facility),
            *self.get_extended_fields(self.get_extended_fields_raw(facility)),
            self.get_is_closed(facility),
        ]

    def get_contributor_custom_fields(
        self, facility: FacilityIndexNewManager
    ) -> List[str]:
        info = next(
            (
                item
                for item in facility.custom_field_info
                if str(item["contributor_id"]) == str(self.contributor_id)
            ),
            None,
        )
        if info is None:
            return [""] * len(self.embed_fields)

        if info["source_type"] == Source.LIST:
            data_values = get_csv_values(info["raw_data"])
            field_indexes = self._get_list_field_indexes(
                info["list_header"]
            )
            return [
                (
                    try_parse_int_from_float(data_values[index])
                    if (index := field_indexes.get(field)) is not None
                    and index < len(data_values)
                    else ""
                )
                for field in self.embed_fields
            ]

        raw_json = parse_raw_data(info["raw_data"])
        return [raw_json.get(field, "") for field in self.embed_fields]

    def get_extended_fields_raw(self, facility: FacilityIndexNewManager):
        return [
            field
            for field in facility.extended_fields
            if self.check_embed_contributor(field["contributor"]["id"])
        ]

    def check_embed_contributor(self, contributor_id: int) -> bool:
        return self.contributor_id == contributor_id

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
            # Last duplicate header wins, matching get_raw_json().
            exact_indexes = {}
            casefold_indexes = {}
            for index, field in enumerate(get_csv_values(list_header)):
                exact_indexes[field] = index
                casefold_indexes[field.casefold()] = index

            field_indexes = {
                field: exact_indexes.get(
                    field,
                    casefold_indexes.get(field.casefold()),
                )
                for field in self.embed_fields
            }
            self._list_field_indexes_by_header[list_header] = field_indexes

        return self._list_field_indexes_by_header[list_header]

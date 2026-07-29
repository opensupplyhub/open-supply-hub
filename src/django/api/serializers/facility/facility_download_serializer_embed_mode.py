from typing import List
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
            *self.get_extended_fields(facility.extended_fields),
            self.get_is_closed(facility),
        ]

    def get_contributor_custom_fields(self, facility: FacilityIndexNewManager):
        infos = [
            info
            for info in facility.custom_field_info
            if str(info["contributor_id"]) == str(self.contributor_id)
        ]
        info = infos[0] if len(infos) > 0 else None
        if info is None:
            return [""] * len(self.embed_fields)

        if info["source_type"] == Source.LIST:
            data_values = get_csv_values(info["raw_data"])
            field_indexes = self.__get_list_field_indexes(
                info["list_header"]
            )

            return [
                data_values[index]
                if (index := field_indexes.get(field)) is not None
                and index < len(data_values)
                else ""
                for field in self.embed_fields
            ]

        raw_json = parse_raw_data(info["raw_data"])
        return [raw_json.get(field, "") for field in self.embed_fields]

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
                for field in self.embed_fields
            }
            self._list_field_indexes_by_header[list_header] = field_indexes

        return self._list_field_indexes_by_header[list_header]

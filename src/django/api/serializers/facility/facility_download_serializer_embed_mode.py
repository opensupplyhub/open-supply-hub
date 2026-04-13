from typing import List
from api.models.facility.facility_manager_index_new \
    import FacilityIndexNewManager
from api.models.embed_field import EmbedField
from api.models import Contributor
from api.helpers.helpers import get_raw_json, parse_raw_data
from api.models.source import Source
from api.serializers.facility.facility_download_serializer_base import (
    FacilityDownloadSerializerBase,
)


class FacilityDownloadSerializerEmbedMode(FacilityDownloadSerializerBase):
    embed_fields = []
    contributor_id = None

    def __init__(self, *args, **kwargs):
        self.contributor_id = int(kwargs.pop("contributor_id", None))
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

    def get_contributor_custom_fields(self, facility: FacilityIndexNewManager):
        infos = [
            info
            for info in facility.custom_field_info
            if str(info["contributor_id"]) == str(self.contributor_id)
        ]
        info = infos[0] if len(infos) > 0 else None
        raw_json = dict()

        if info is not None:
            if info["source_type"] == Source.LIST:
                raw_json = get_raw_json(info["raw_data"], info["list_header"])
            else:
                raw_json = parse_raw_data(info["raw_data"])

        res = [raw_json.get(field, "") for field in self.embed_fields]
        return res

    def check_embed_contributor(self, contributor_id: int) -> bool:
        return self.contributor_id == contributor_id

    def get_extended_fields_raw(self, facility: FacilityIndexNewManager):
        return [
            field
            for field in facility.extended_fields
            if self.check_embed_contributor(field["contributor"]["id"])
        ]

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

from typing import Any, List
from api.models.facility.facility_index import FacilityIndex
from api.models.facility.facility_manager_index_new import (
    FacilityIndexNewManager,
)
from countries.lib.countries import COUNTRY_NAMES
from api.csv_download import format_download_extended_fields
from api.helpers.helpers import parse_download_date
from rest_framework.serializers import Serializer, SerializerMethodField


class FacilityDownloadSerializerBase(Serializer):
    row = SerializerMethodField()

    class Meta:
        model = FacilityIndex()
        fields = "rows"

    EXTENDED_FIELDS_HEADERS = [
        "number_of_workers",
        "parent_company",
        "processing_type_facility_type_raw",
        "facility_type",
        "processing_type",
        "product_type",
    ]
    COMMON_HEADERS = [
        "os_id",
        "contribution_date",
        "name",
        "address",
        "country_code",
        "country_name",
        "lat",
        "lng",
        "sector",
    ]
    IS_CLOSED_HEADER = "is_closed"

    def get_common_row(self, facility: FacilityIndexNewManager):
        return [
            facility.id,
            self.get_contribution_date(facility),
            self.get_name(facility),
            facility.address,
            facility.country_code,
            self.get_country_name(facility),
            *self.get_location(facility),
            self.get_sector(facility),
        ]

    @staticmethod
    def get_contribution_date(facility: FacilityIndexNewManager) -> str:
        created_at = facility.created_from_info["created_at"]
        return parse_download_date(created_at)

    @staticmethod
    def get_name(facility: FacilityIndexNewManager) -> str:
        claim = facility.approved_claim
        if claim and claim.get("facility_name_english"):
            return claim.get("facility_name_english")
        return facility.name

    @staticmethod
    def get_country_name(facility: FacilityIndexNewManager) -> str:
        return COUNTRY_NAMES.get(facility.country_code, "")

    @staticmethod
    def get_location(facility: FacilityIndexNewManager) -> List[str]:
        return list(reversed(facility.location.coords))

    def get_sector(self, facility: FacilityIndex):
        return self.join(facility.sector)

    def get_extended_fields(self, fields) -> List[Any]:
        extended_fields = [[], [], [], [], [], []]
        format_download_extended_fields(fields, extended_fields)

        return list(map("|".join, extended_fields))

    @staticmethod
    def get_is_closed(facility: FacilityIndexNewManager) -> str:
        return str(
            facility.is_closed if facility.is_closed is not None else False
        )

    @staticmethod
    def join(arr: List[Any]) -> str:
        return "|".join([item.title() for item in arr])

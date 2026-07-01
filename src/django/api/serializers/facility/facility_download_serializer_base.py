from typing import Any, List

from api.csv_download import format_download_extended_fields
from api.helpers.helpers import parse_download_date
from api.models.facility.facility_index import FacilityIndex
from api.models.facility.facility_manager_index_new import \
    FacilityIndexNewManager
from api.services.masked_contributors import MaskedContributors
from countries.lib.countries import COUNTRY_NAMES
from rest_framework.serializers import Serializer, SerializerMethodField


class FacilityDownloadSerializerBase(Serializer):
    """Shared CSV row helpers for full and embed facility downloads."""

    row = SerializerMethodField()

    def __init__(self, *args, masked_contributors=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.masked_contributors = (
            masked_contributors or MaskedContributors()
        )

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
        """Return the leading columns shared by every download format."""
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
        """Return the facility creation date formatted for CSV export."""
        created_at = facility.created_from_info["created_at"]
        return parse_download_date(created_at)

    @staticmethod
    def get_name(facility: FacilityIndexNewManager) -> str:
        """Return the English claim name when present, otherwise the facility
        name."""
        claim = facility.approved_claim
        if claim and claim.get("facility_name_english"):
            return claim.get("facility_name_english")
        return facility.name

    @staticmethod
    def get_country_name(facility: FacilityIndexNewManager) -> str:
        """Return the display name for the facility country code."""
        return COUNTRY_NAMES.get(facility.country_code, "")

    @staticmethod
    def get_location(facility: FacilityIndexNewManager) -> List[str]:
        """Return latitude and longitude as ``[lat, lng]``."""
        return list(reversed(facility.location.coords))

    def get_sector(self, facility: FacilityIndex):
        """Return pipe-separated, title-cased sector values."""
        return self.join(facility.sector)

    def get_extended_fields(self, fields) -> List[Any]:
        """Return the six standard extended-field columns, joined with
        ``|``."""
        extended_fields = [[], [], [], [], [], []]
        format_download_extended_fields(fields, extended_fields)

        return list(map("|".join, extended_fields))

    @staticmethod
    def get_is_closed(facility: FacilityIndexNewManager) -> str:
        """Return ``"True"`` or ``"False"`` for the facility closed status."""
        return str(
            facility.is_closed
            if facility.is_closed is not None
            else False
        )

    @staticmethod
    def join(arr: List[Any]) -> str:
        """Join list items with ``|``, applying title case to each."""
        return "|".join([item.title() for item in arr])

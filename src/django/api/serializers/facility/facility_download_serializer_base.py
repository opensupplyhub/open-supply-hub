from typing import Any, List
from api.models.facility.facility_index import FacilityIndex
from api.models.facility.facility_manager_index_new import (
    FacilityIndexNewManager,
)
from countries.lib.countries import COUNTRY_NAMES
from api.csv_download import (
    format_download_extended_fields,
    format_download_claimed_fields,
    CLAIMED_DOWNLOAD_FIELDS,
)
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

    CLAIMED_FIELDS_HEADERS = [
        "claim_created_at",
        "claim_contact_person",
        "claim_job_title",
        "claim_company_name",
        "claim_name_in_native_language",
        "claim_company_website",
        "claim_website",
        "claim_company_phone",
        "claim_point_of_contact",
        "claim_linkedin_profile",
        "claim_office_name",
        "claim_office_address",
        "claim_office_country_code",
        "claim_office_phone_number",
        "claim_description",
        "claim_certifications_standards_regulations",
        "claim_affiliations",
        "claim_minimum_order_quantity",
        "claim_average_lead_time",
        "claim_female_workers_percentage",
        "claim_industry_sectors",
        "claim_location_types",
        "claim_other_location_type",
        "claim_product_types",
        "claim_processing_types",
        "claim_parent_company",
        "claim_number_of_workers",
    ]

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

    def get_claimed_fields(
            self,
            facility: FacilityIndexNewManager
    ) -> List[str]:
        output = [''] * len(CLAIMED_DOWNLOAD_FIELDS)
        claim = facility.approved_claim
        if claim:
            format_download_claimed_fields(claim, output)
        return output

    @staticmethod
    def get_is_closed(facility: FacilityIndexNewManager) -> str:
        return str(
            facility.is_closed if facility.is_closed is not None else False
        )

    @staticmethod
    def join(arr: List[Any]) -> str:
        return "|".join([item.title() for item in arr])

from django.test import TestCase

from api.models.contributor.contributor import Contributor
from api.models.embed_config import EmbedConfig
from api.models.embed_field import EmbedField
from api.models.facility.facility_index import FacilityIndex
from api.serializers.facility.facility_download_serializer_embed_mode import (
    FacilityDownloadSerializerEmbedMode,
)

CLAIM_HEADERS = [
    "claim_created_at",
    "claim_contact_person",
    "claim_job_title",
    "claim_company_name",
    "claim_name_in_native_language",
    "claim_company_website",
    "claim_website",
    "claim_company_phone",
    "claim_point_of_contact",
    "claim_point_of_contact_email",
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

EMPTY_CLAIM_VALUES = [""] * len(CLAIM_HEADERS)


class FacilityDownloadSerializerEmbedModeTest(TestCase):
    fixtures = ["facilities_index", "contributors", "users"]

    def setUp(self):
        self.facility_one = FacilityIndex.objects.get(id="1")

        self.embed_config = EmbedConfig.objects.create()
        self.contributor = Contributor.objects.get(id=1)
        self.contributor.embed_config = self.embed_config
        self.contributor.save()
        self.embed_one = EmbedField.objects.create(
            embed_config=self.embed_config,
            order=0,
            column_name="extra_1",
            display_name="ExtraOne",
            visible=True,
            searchable=True,
        )
        self.embed_two = EmbedField.objects.create(
            embed_config=self.embed_config,
            order=1,
            column_name="extra_2",
            display_name="ExtraTwo",
            visible=True,
            searchable=True,
        )
        self.embed_three = EmbedField.objects.create(
            embed_config=self.embed_config,
            order=2,
            column_name="parent_company",
            display_name="Parent Company",
            visible=True,
            searchable=True,
        )
        self.embed_four = EmbedField.objects.create(
            embed_config=self.embed_config,
            order=3,
            column_name="extra_3",
            display_name="ExtraThree",
            visible=False,
            searchable=False,
        )

    def test_get_headers(self):
        contributor_id = "1"
        serializer = FacilityDownloadSerializerEmbedMode(
            contributor_id=contributor_id
        )
        headers = serializer.get_headers()
        expected_headers = [
            "os_id",
            "contribution_date",
            "name",
            "address",
            "country_code",
            "country_name",
            "lat",
            "lng",
            "sector",
            "extra_1",
            "extra_2",
            "number_of_workers",
            "parent_company",
            "processing_type_facility_type_raw",
            "facility_type",
            "processing_type",
            "product_type",
            *CLAIM_HEADERS,
            "is_closed",
        ]
        self.assertEqual(headers, expected_headers)

    def test_get_row(self):
        contributor_id = "1"
        serializer = FacilityDownloadSerializerEmbedMode(
            contributor_id=contributor_id
        )
        row = serializer.get_row(self.facility_one)
        expected_row = [
            "1",
            "2022-05-18",
            "First Facility",
            "First Facility Address",
            "US",
            "United States",
            0.0,
            0.0,
            "Test Sector",
            "Extra 1 custom field data",
            "Extra 2 custom field data",
            "1",
            "Parent Company Service Provider A",
            "Raw Data",
            "Matched facility type value one Service Provider A|"
            "Matched facility type value two Service Provider A",
            "Matched processing type value one Service Provider A|"
            "Matched processing type value two Service Provider A",
            "Product Type Service Provider A",
            *EMPTY_CLAIM_VALUES,
            "False",
        ]
        self.assertEqual(row, expected_row)

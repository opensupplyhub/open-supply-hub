from django.test import TestCase

from api.models.facility.facility_index import FacilityIndex
from api.serializers.facility.facility_download_serializer import (
    FacilityDownloadSerializer,
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


class FacilityDownloadSerializerTest(TestCase):
    fixtures = ["facilities_index"]

    def setUp(self):
        self.facility_one = FacilityIndex.objects.get(id="1")
        self.facility_two = FacilityIndex.objects.get(id="2")
        self.facility_three = FacilityIndex.objects.get(id="3")

    def test_get_headers(self):
        serializer = FacilityDownloadSerializer()
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
            "contributor (list)",
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
        serializer = FacilityDownloadSerializer()
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
            "A Service Provider|A Factory / Facility|Brand A",
            "1|101-500",
            "Parent Company Service Provider A|Parent Company Factory A",
            "Raw Data",
            "Matched facility type value one Service Provider A|"
            "Matched facility type value two Service Provider A|"
            "Matched facility type value one Factory A",
            "Matched processing type value one Service Provider A|"
            "Matched processing type value two Service Provider A|"
            "Matched processing type value one Factory A",
            "Product Type Service Provider A|Product Type Factory A",
            *EMPTY_CLAIM_VALUES,
            "False",
        ]
        self.assertEqual(row, expected_row)

    def test_get_row_with_claim_from_contributor_with_extended_fields(self):
        serializer = FacilityDownloadSerializer()
        row = serializer.get_row(self.facility_two)
        expected_row = [
            "2",
            "2020-02-22",
            "Second Facility Name English",
            "Second Facility Address",
            "IN",
            "India",
            0.0,
            0.0,
            "Test Sector",
            "Factory A (Claimed)|"
            "A Service Provider|"
            "A Factory / Facility|"
            "Brand A",
            "101-500",
            "Parent Company Factory A",
            "Raw Data",
            "Matched facility type value one Factory A",
            "Matched processing type value one Factory A",
            "Product Type Factory A",
            *EMPTY_CLAIM_VALUES,
            "False",
        ]
        self.assertEqual(row, expected_row)

    def test_get_row_with_claim_from_contributor_without_extended_fields(self):
        serializer = FacilityDownloadSerializer()
        row = serializer.get_row(self.facility_three)
        expected_row = [
            "3",
            "2020-02-22",
            "Third Facility",
            "Third Facility Address",
            "CN",
            "China",
            0.0,
            0.0,
            "Test Sector",
            "Factory A (Claimed)|A Service Provider|A Factory / Facility",
            "",
            "",
            "",
            "",
            "",
            "",
            *EMPTY_CLAIM_VALUES,
            "False",
        ]
        self.assertEqual(row, expected_row)

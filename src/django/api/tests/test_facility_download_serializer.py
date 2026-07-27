import copy
from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.gis.geos import Point
from django.test import TestCase

from api.models.facility.facility_index import FacilityIndex
from api.models.partner_field import PartnerField
from api.models.wage_indicator_country_data import WageIndicatorCountryData
from api.serializers.facility.facility_download_serializer import (
    FacilityDownloadSerializer,
)

CLAIM_HEADERS = [
    "claim_created_at",
    "claim_name_in_native_language",
    "claim_company_website",
    "claim_company_phone",
    "claim_point_of_contact",
    "claim_point_of_contact_email",
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
    "claim_opening_date",
    "claim_closing_date",
    "claim_estimated_annual_throughput_kg_year",
    "claim_energy_coal_j",
    "claim_energy_natural_gas_j",
    "claim_energy_diesel_j",
    "claim_energy_kerosene_j",
    "claim_energy_biomass_j",
    "claim_energy_charcoal_j",
    "claim_energy_animal_waste_j",
    "claim_energy_electricity_mwh",
    "claim_energy_other_j",
]

EMPTY_CLAIM_VALUES = [""] * len(CLAIM_HEADERS)

PARTNER_FIELD_HEADERS: list = [
    "mit_living_wage.county_link",
    "mit_living_wage.county_link_text",
    "wage_indicator.living_wage_link_national",
    "wage_indicator.living_wage_link_national_text",
    "wage_indicator.minimum_wage_link_english",
    "wage_indicator.minimum_wage_link_english_text",
    "wage_indicator.minimum_wage_link_national",
    "wage_indicator.minimum_wage_link_national_text",
]

EMPTY_PARTNER_FIELD_VALUES: list = [""] * len(PARTNER_FIELD_HEADERS)


class FacilityDownloadSerializerTest(TestCase):
    """CSV header and row output for full facility downloads."""

    fixtures = ["facilities_index"]

    def setUp(self):
        """Load fixture facilities; clear wage-indicator data for empty
        partner cells."""
        # Migration 0193 seeds WageIndicatorCountryData for every country
        # these fixtures use. Clear it so partner-field assertions expect
        # empty wage_indicator.* cells instead of migration-provided URLs.
        WageIndicatorCountryData.objects.all().delete()
        self.facility_one = FacilityIndex.objects.get(id="1")
        self.facility_two = FacilityIndex.objects.get(id="2")
        self.facility_three = FacilityIndex.objects.get(id="3")

    def test_get_headers(self):
        """Returns the full header list, including claim and partner-field
        columns."""
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
            *PARTNER_FIELD_HEADERS,
        ]
        self.assertEqual(headers, expected_headers)

    def test_get_row(self):
        """Builds a complete row for an unclaimed, multi-contributor
        facility."""
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
            *EMPTY_PARTNER_FIELD_VALUES,
        ]
        self.assertEqual(row, expected_row)

    def test_get_row_with_claim_from_contributor_with_extended_fields(self):
        """Uses the English claim name and labels the claiming contributor."""
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
            *EMPTY_PARTNER_FIELD_VALUES,
        ]
        self.assertEqual(row, expected_row)

    def test_get_row_uses_claim_address_when_present(self):
        """Uses the claim address for the address column when the approved
        claim provides one."""
        serializer = FacilityDownloadSerializer()
        self.facility_two.approved_claim["facility_address"] = (
            "Claimed Facility Address"
        )
        row = serializer.get_row(self.facility_two)
        self.assertEqual(row[3], "Claimed Facility Address")

    def test_get_address_falls_back_when_claim_address_empty(self):
        """Falls back to the facility address when the claim address is
        empty or the facility is unclaimed."""
        self.facility_two.approved_claim["facility_address"] = ""
        self.assertEqual(
            FacilityDownloadSerializer.get_address(self.facility_two),
            self.facility_two.address,
        )
        self.assertEqual(
            FacilityDownloadSerializer.get_address(self.facility_one),
            self.facility_one.address,
        )

    def test_partner_fields_headers_flatten_object_schema(self):
        """Object fields become dotted headers; primitive fields keep a single
        column."""
        partner_fields = [
            SimpleNamespace(
                name="bsci_audit",
                type=PartnerField.OBJECT,
                json_schema={
                    "properties": {
                        "submission_date": {"type": "string"},
                        "expiration_date": {"type": "string"},
                    }
                },
            ),
            SimpleNamespace(
                name="estimated_emissions",
                type=PartnerField.INT,
                json_schema=None,
            ),
        ]
        serializer = FacilityDownloadSerializer(partner_fields=partner_fields)
        headers = serializer.get_partner_fields_headers()
        self.assertEqual(
            headers,
            [
                "bsci_audit.submission_date",
                "bsci_audit.expiration_date",
                "estimated_emissions",
            ],
        )

    @patch(
        "api.serializers.facility.facility_download_serializer."
        "get_cached_all_partner_fields"
    )
    def test_headers_exclude_fields_unavailable_in_downloads(
        self, mock_get_fields
    ):
        """Partner fields flagged ``available_in_data_downloads=False`` are not
        included in the download headers."""
        mock_get_fields.return_value = [
            SimpleNamespace(
                name="visible_field",
                type=PartnerField.STRING,
                json_schema=None,
                active=True,
                available_in_data_downloads=True,
                system_field=False,
            ),
            SimpleNamespace(
                name="hidden_field",
                type=PartnerField.STRING,
                json_schema=None,
                active=True,
                available_in_data_downloads=False,
                system_field=False,
            ),
        ]
        serializer = FacilityDownloadSerializer()
        headers = serializer.get_partner_fields_headers()
        self.assertIn("visible_field", headers)
        self.assertNotIn("hidden_field", headers)

    @patch(
        "api.serializers.facility.facility_download_serializer."
        "get_cached_all_partner_fields"
    )
    def test_headers_exclude_inactive_fields(self, mock_get_fields):
        """Inactive partner fields are excluded even when available in
        downloads."""
        mock_get_fields.return_value = [
            SimpleNamespace(
                name="inactive_field",
                type=PartnerField.STRING,
                json_schema=None,
                active=False,
                available_in_data_downloads=True,
                system_field=False,
            ),
        ]
        serializer = FacilityDownloadSerializer()
        headers = serializer.get_partner_fields_headers()
        self.assertNotIn("inactive_field", headers)

    def test_partner_fields_row_matches_object_and_primitive(self):
        """Maps object and primitive values to cells; missing fields become
        empty."""
        partner_fields = [
            SimpleNamespace(
                name="bsci_audit",
                type=PartnerField.OBJECT,
                json_schema={
                    "properties": {
                        "submission_date": {"type": "string"},
                        "expiration_date": {"type": "string"},
                    }
                },
            ),
            SimpleNamespace(
                name="estimated_emissions",
                type=PartnerField.INT,
                json_schema=None,
            ),
            SimpleNamespace(
                name="unused_partner_field",
                type=PartnerField.STRING,
                json_schema=None,
            ),
        ]
        extended_fields = [
            {
                "field_name": "bsci_audit",
                "value": {
                    "raw_values": {
                        "submission_date": "2024-10-15",
                        "expiration_date": "2026-10-15",
                    }
                },
                "contributor": {"id": 1},
            },
            {
                "field_name": "estimated_emissions",
                "value": {"raw_value": 13},
                "contributor": {"id": 1},
            },
        ]
        serializer = FacilityDownloadSerializer(partner_fields=partner_fields)
        row = serializer.get_partner_fields_row(extended_fields)
        self.assertEqual(
            row,
            ["2024-10-15", "2026-10-15", "13", ""],
        )

    def test_partner_fields_expand_nested_object_schema(self):
        """Headers and cells follow nested JSON Schema paths."""
        amfori_schema = {
            "type": "object",
            "title": "Amfori Compliance Status",
            "properties": {
                "bepi_audit": {
                    "type": "object",
                    "properties": {
                        "expiration_date": {
                            "type": "string",
                            "format": "date",
                        },
                        "submission_date": {
                            "type": "string",
                            "format": "date",
                        },
                    },
                },
                "bsci_audit": {
                    "type": "object",
                    "properties": {
                        "expiration_date": {
                            "type": "string",
                            "format": "date",
                        },
                        "submission_date": {
                            "type": "string",
                            "format": "date",
                        },
                    },
                },
                "environmental_risk_assessment": {
                    "type": "object",
                    "properties": {
                        "completion_date": {
                            "type": "string",
                            "format": "date",
                        },
                        "expiration_date": {
                            "type": "string",
                            "format": "date",
                        },
                    },
                },
            },
        }
        partner_fields = [
            SimpleNamespace(
                name="amfori_compliance_status",
                type=PartnerField.OBJECT,
                json_schema=amfori_schema,
            ),
        ]
        extended_fields = [
            {
                "field_name": "amfori_compliance_status",
                "value": {
                    "raw_values": {
                        "bepi_audit": {
                            "submission_date": "2024-11-20",
                            "expiration_date": "2026-11-20",
                        },
                        "bsci_audit": {
                            "submission_date": "2024-10-15",
                        },
                        "environmental_risk_assessment": {
                            "completion_date": "2024-12-01",
                            "expiration_date": "2026-12-01",
                        },
                    }
                },
                "contributor": {"id": 1},
            },
        ]
        serializer = FacilityDownloadSerializer(partner_fields=partner_fields)
        headers = serializer.get_partner_fields_headers()
        row = serializer.get_partner_fields_row(extended_fields)
        self.assertEqual(
            headers,
            [
                "amfori_compliance_status.bepi_audit.expiration_date",
                "amfori_compliance_status.bepi_audit.submission_date",
                "amfori_compliance_status.bsci_audit.expiration_date",
                "amfori_compliance_status.bsci_audit.submission_date",
                "amfori_compliance_status"
                ".environmental_risk_assessment.completion_date",
                "amfori_compliance_status"
                ".environmental_risk_assessment.expiration_date",
            ],
        )
        self.assertEqual(
            row,
            [
                "2026-11-20",
                "2024-11-20",
                "",
                "2024-10-15",
                "2024-12-01",
                "2026-12-01",
            ],
        )

    def test_partner_fields_row_skips_non_dict_value(self):
        """Skips partner-field entries whose value is not a dict."""
        partner_fields = [
            SimpleNamespace(
                name='bsci_audit',
                type=PartnerField.OBJECT,
                json_schema={
                    'properties': {
                        'submission_date': {'type': 'string'},
                    }
                },
            ),
        ]
        extended_fields = [
            {
                'field_name': 'bsci_audit',
                'value': 'not a dict',
                'contributor': {'id': 1},
            },
            {
                'field_name': 'bsci_audit',
                'value': ['also', 'not', 'a', 'dict'],
                'contributor': {'id': 2},
            },
            {
                'field_name': 'bsci_audit',
                'value': 42,
                'contributor': {'id': 3},
            },
        ]
        serializer = FacilityDownloadSerializer(partner_fields=partner_fields)
        row = serializer.get_partner_fields_row(extended_fields)
        self.assertEqual(row, [''])

    def test_partner_fields_row_does_not_mutate_original_data(self):
        """Leaves extended_fields raw_values unchanged after building the
        row."""
        partner_fields = [
            SimpleNamespace(
                name='bsci_audit',
                type=PartnerField.OBJECT,
                json_schema={
                    'properties': {
                        'submission_date': {'type': 'string'},
                        'expiration_date': {
                            'type': 'string',
                            'default': 'N/A',
                        },
                    }
                },
            ),
        ]
        extended_fields = [
            {
                'field_name': 'bsci_audit',
                'value': {
                    'raw_values': {
                        'submission_date': '2024-10-15',
                    }
                },
                'contributor': {'id': 1},
            },
        ]
        original = copy.deepcopy(extended_fields)
        serializer = FacilityDownloadSerializer(partner_fields=partner_fields)
        serializer.get_partner_fields_row(extended_fields)
        self.assertEqual(
            extended_fields[0]['value']['raw_values'],
            original[0]['value']['raw_values'],
        )

    def test_partner_fields_row_fills_schema_defaults_for_missing_values(self):
        """Fills missing object properties from JSON Schema defaults."""
        partner_fields = [
            SimpleNamespace(
                name='bsci_audit',
                type=PartnerField.OBJECT,
                json_schema={
                    'properties': {
                        'submission_date': {'type': 'string'},
                        'expiration_date': {
                            'type': 'string',
                            'default': 'N/A',
                        },
                        'rating': {
                            'type': 'string',
                            'default': 'unrated',
                        },
                    }
                },
            ),
        ]
        extended_fields = [
            {
                'field_name': 'bsci_audit',
                'value': {
                    'raw_values': {
                        'submission_date': '2024-10-15',
                    }
                },
                'contributor': {'id': 1},
            },
        ]
        serializer = FacilityDownloadSerializer(partner_fields=partner_fields)
        row = serializer.get_partner_fields_row(extended_fields)
        self.assertEqual(row, ['2024-10-15', 'N/A', 'unrated'])

    def test_get_row_with_claim_from_contributor_without_extended_fields(self):
        """Builds a row when only the claimer's extended fields are present."""
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
            *EMPTY_PARTNER_FIELD_VALUES,
        ]
        self.assertEqual(row, expected_row)

    @patch.object(
        FacilityDownloadSerializer,
        "get_claimed_fields",
        return_value=[""] * len(CLAIM_HEADERS),
    )
    @patch.object(
        FacilityDownloadSerializer,
        "get_partner_fields_row",
        return_value=[],
    )
    @patch.object(
        FacilityDownloadSerializer,
        "get_mit_living_wage_row",
        return_value=["", ""],
    )
    @patch.object(
        FacilityDownloadSerializer,
        "get_wage_indicator_row",
        return_value=[""] * 6,
    )
    def test_claimed_facility_includes_all_contributors_extended_fields(
        self, _wage, _mit, _partner, _claim
    ):
        """Includes extended fields from every contributor, not only the
        claimer."""
        facility = SimpleNamespace(
            id="MOCK_1",
            name="Mock Facility",
            address="1 Mock St",
            country_code="US",
            location=Point(0.0, 0.0),
            sector=["Apparel"],
            is_closed=False,
            created_from_info={"created_at": "2024-01-01T00:00:00+00:00"},
            approved_claim={
                "id": 1,
                "contributor_id": 100,
                "contributor": {"name": "Claiming Corp"},
                "facility_name_english": None,
            },
            contributors=[
                {
                    "id": 200,
                    "name": "Other Corp",
                    "contrib_type": "Brand/Retailer",
                    "should_display_associations": True,
                },
            ],
            extended_fields=[
                {
                    "id": 1,
                    "field_name": "number_of_workers",
                    "value": {"min": 50, "max": 100},
                    "contributor": {"id": 200, "name": "Other Corp"},
                },
                {
                    "id": 2,
                    "field_name": "number_of_workers",
                    "value": {"min": 500, "max": 1000},
                    "contributor": {"id": 100, "name": "Claiming Corp"},
                },
                {
                    "id": 3,
                    "field_name": "parent_company",
                    "value": {"name": "Other Parent Co"},
                    "contributor": {"id": 200, "name": "Other Corp"},
                },
            ],
        )
        serializer = FacilityDownloadSerializer()
        row = serializer.get_row(facility)
        self.assertEqual(row[10], "50-100|500-1000")
        self.assertEqual(row[11], "Other Parent Co")

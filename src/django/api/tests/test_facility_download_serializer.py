from types import SimpleNamespace

from django.test import TestCase

from api.models.facility.facility_index import FacilityIndex
from api.models.partner_field import PartnerField
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
]

EMPTY_PARTNER_FIELD_VALUES: list = [""] * len(PARTNER_FIELD_HEADERS)


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
            *PARTNER_FIELD_HEADERS,
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
            *EMPTY_PARTNER_FIELD_VALUES,
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
            *EMPTY_PARTNER_FIELD_VALUES,
        ]
        self.assertEqual(row, expected_row)

    def test_partner_fields_headers_flatten_object_schema(self):
        partner_fields = [
            SimpleNamespace(
                name='bsci_audit',
                type=PartnerField.OBJECT,
                json_schema={
                    'properties': {
                        'submission_date': {'type': 'string'},
                        'expiration_date': {'type': 'string'},
                    }
                },
            ),
            SimpleNamespace(
                name='estimated_emissions',
                type=PartnerField.INT,
                json_schema=None,
            ),
        ]
        serializer = FacilityDownloadSerializer()
        headers = serializer.get_partner_fields_headers(partner_fields)
        self.assertEqual(
            headers,
            [
                'bsci_audit.submission_date',
                'bsci_audit.expiration_date',
                'estimated_emissions',
            ],
        )

    def test_partner_fields_row_matches_object_and_primitive(self):
        partner_fields = [
            SimpleNamespace(
                name='bsci_audit',
                type=PartnerField.OBJECT,
                json_schema={
                    'properties': {
                        'submission_date': {'type': 'string'},
                        'expiration_date': {'type': 'string'},
                    }
                },
            ),
            SimpleNamespace(
                name='estimated_emissions',
                type=PartnerField.INT,
                json_schema=None,
            ),
            SimpleNamespace(
                name='unused_partner_field',
                type=PartnerField.STRING,
                json_schema=None,
            ),
        ]
        extended_fields = [
            {
                'field_name': 'bsci_audit',
                'value': {
                    'raw_values': {
                        'submission_date': '2024-10-15',
                        'expiration_date': '2026-10-15',
                    }
                },
                'contributor': {'id': 1},
            },
            {
                'field_name': 'estimated_emissions',
                'value': {'raw_value': 13},
                'contributor': {'id': 1},
            },
        ]
        serializer = FacilityDownloadSerializer()
        row = serializer.get_partner_fields_row(
            extended_fields, partner_fields
        )
        self.assertEqual(
            row,
            ['2024-10-15', '2026-10-15', '13', ''],
        )

    def test_partner_fields_expand_nested_object_schema(self):
        amfori_schema = {
            'type': 'object',
            'title': 'Amfori Compliance Status',
            'properties': {
                'bepi_audit': {
                    'type': 'object',
                    'properties': {
                        'expiration_date': {
                            'type': 'string',
                            'format': 'date',
                        },
                        'submission_date': {
                            'type': 'string',
                            'format': 'date',
                        },
                    },
                },
                'bsci_audit': {
                    'type': 'object',
                    'properties': {
                        'expiration_date': {
                            'type': 'string',
                            'format': 'date',
                        },
                        'submission_date': {
                            'type': 'string',
                            'format': 'date',
                        },
                    },
                },
                'environmental_risk_assessment': {
                    'type': 'object',
                    'properties': {
                        'completion_date': {
                            'type': 'string',
                            'format': 'date',
                        },
                        'expiration_date': {
                            'type': 'string',
                            'format': 'date',
                        },
                    },
                },
            },
        }
        partner_fields = [
            SimpleNamespace(
                name='amfori_compliance_status',
                type=PartnerField.OBJECT,
                json_schema=amfori_schema,
            ),
        ]
        extended_fields = [
            {
                'field_name': 'amfori_compliance_status',
                'value': {
                    'raw_values': {
                        'bepi_audit': {
                            'submission_date': '2024-11-20',
                            'expiration_date': '2026-11-20',
                        },
                        'bsci_audit': {
                            'submission_date': '2024-10-15',
                        },
                        'environmental_risk_assessment': {
                            'completion_date': '2024-12-01',
                            'expiration_date': '2026-12-01',
                        },
                    }
                },
                'contributor': {'id': 1},
            },
        ]
        serializer = FacilityDownloadSerializer()
        headers = serializer.get_partner_fields_headers(partner_fields)
        row = serializer.get_partner_fields_row(
            extended_fields, partner_fields
        )
        self.assertEqual(
            headers,
            [
                'amfori_compliance_status.bepi_audit.expiration_date',
                'amfori_compliance_status.bepi_audit.submission_date',
                'amfori_compliance_status.bsci_audit.expiration_date',
                'amfori_compliance_status.bsci_audit.submission_date',
                'amfori_compliance_status'
                '.environmental_risk_assessment.completion_date',
                'amfori_compliance_status'
                '.environmental_risk_assessment.expiration_date',
            ],
        )
        self.assertEqual(
            row,
            [
                '2026-11-20',
                '2024-11-20',
                '',
                '2024-10-15',
                '2024-12-01',
                '2026-12-01',
            ],
        )

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
            *EMPTY_PARTNER_FIELD_VALUES,
        ]
        self.assertEqual(row, expected_row)

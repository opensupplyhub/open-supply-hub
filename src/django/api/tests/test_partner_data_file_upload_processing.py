import json

from django.contrib.gis.geos import Point
from django.test import TestCase
from unittest.mock import Mock, patch

from rest_framework import status

from api.models.contributor.contributor import Contributor
from api.models.facility.facility import Facility
from api.models.facility.facility_list import FacilityList
from api.models.facility.facility_list_item import FacilityListItem
from api.models.partner_field import PartnerField
from api.models.source import Source
from api.models.user import User
from api.moderation_event_actions.creation.location_contribution.location_contribution import (  # noqa: E501
    LocationContribution,
)
from api.moderation_event_actions.creation.moderation_event_creator import (
    ModerationEventCreator,
)
from api.management.commands.process_partner_data_file_uploads import (
    ColumnMapping,
    PartnerFieldSheetParser,
    PartnerPatchModerationEventCreator,
)
from api.tests.test_data import geocoding_data

WORLDLY_ASSESSMENT_SCHEMA = {
    "type": "object",
    "title": "Worldly Assessments Data Update",
    "properties": {
        "fdm_assessment": {
            "type": "object",
            "properties": {
                "assessment_url": {
                    "type": "string",
                    "format": "uri",
                },
                "reporting_year": {
                    "type": "integer",
                },
                "verification_status": {
                    "enum": ["verified", "unverified", "pending"],
                    "type": "string",
                },
            },
        },
        "fem_assessment": {
            "type": "object",
            "properties": {
                "assessment_url": {
                    "type": "string",
                    "format": "url",
                },
                "reporting_year": {
                    "type": "integer",
                },
            },
        },
    },
}


class PartnerDataFileUploadProcessingTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(email="partner-upload@test.com")
        self.contributor = Contributor.objects.create(
            admin=self.user,
            name="Partner Upload Contributor",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )
        self.string_field = PartnerField.objects.create(
            name="custom_partner_field",
            type=PartnerField.STRING,
            label="Custom Partner Field",
        )
        self.int_field = PartnerField.objects.create(
            name="estimated_annual_energy_consumption",
            type=PartnerField.INT,
            label="Estimated Annual Energy Consumption",
        )
        self.float_field = PartnerField.objects.create(
            name="estimated_emissions_activity",
            type=PartnerField.FLOAT,
            label="Estimated Emissions Activity",
        )
        self.worldly_field = PartnerField.objects.create(
            name="worldly_assessment_data",
            type=PartnerField.OBJECT,
            label="Worldly Assessment Data",
            json_schema=WORLDLY_ASSESSMENT_SCHEMA,
        )
        self.contributor.partner_fields.add(
            self.string_field,
            self.int_field,
            self.float_field,
            self.worldly_field,
        )

        facility_list = FacilityList.objects.create(
            header="header",
            file_name="one",
            name="Partner Upload List",
        )
        source = Source.objects.create(
            source_type=Source.LIST,
            facility_list=facility_list,
            contributor=self.contributor,
        )
        list_item = FacilityListItem.objects.create(
            name="Gamma Tech Manufacturing Plant",
            address="1574 Quantum Avenue, Building 4B, Technopolis",
            country_code="US",
            sector=["Apparel"],
            row_index=1,
            status=FacilityListItem.CONFIRMED_MATCH,
            source=source,
        )
        self.facility = Facility.objects.create(
            name=list_item.name,
            address=list_item.address,
            country_code=list_item.country_code,
            location=Point(-75.158, 39.961),
            created_from=list_item,
        )

    def test_validate_headers_reports_multiple_issues(self):
        header_map = PartnerFieldSheetParser.build_header_map(["Bad-Column"])
        with self.assertRaises(ValueError) as context:
            PartnerFieldSheetParser.validate_headers(header_map)

        message = str(context.exception)
        self.assertIn("snake_case", message)
        self.assertIn("os_id", message)

        header_map = PartnerFieldSheetParser.build_header_map(["os_id"])
        with self.assertRaises(ValueError) as context:
            PartnerFieldSheetParser.validate_headers(header_map)

        self.assertIn("at least one partner field", str(context.exception))

    def test_validate_headers_requires_os_id(self):
        header_map = PartnerFieldSheetParser.build_header_map(
            ["custom_partner_field"]
        )
        with self.assertRaises(ValueError) as context:
            PartnerFieldSheetParser.validate_headers(header_map)

        self.assertIn("os_id", str(context.exception))

    def test_validate_headers_rejects_invalid_snake_case(self):
        header_map = PartnerFieldSheetParser.build_header_map(
            ["os_id", "Bad-Column"]
        )
        with self.assertRaises(ValueError) as context:
            PartnerFieldSheetParser.validate_headers(header_map)

        self.assertIn("snake_case", str(context.exception))

    def test_validate_headers_rejects_non_normalized_partner_headers(self):
        header_map = PartnerFieldSheetParser.build_header_map(
            ["OS ID", "custom_partner_field"]
        )
        with self.assertRaises(ValueError) as context:
            PartnerFieldSheetParser.validate_headers(header_map)

        self.assertIn("OS ID", str(context.exception))
        self.assertIn("snake_case", str(context.exception))

    def test_build_header_map_does_not_normalize_headers(self):
        header_map = PartnerFieldSheetParser.build_header_map(
            ["os_id", "custom_partner_field"]
        )

        self.assertEqual(
            header_map,
            {"os_id": 0, "custom_partner_field": 1},
        )

    def test_build_header_map_rejects_duplicate_headers(self):
        with self.assertRaises(ValueError) as context:
            PartnerFieldSheetParser.build_header_map(
                [
                    "os_id",
                    "custom_partner_field",
                    "os_id",
                    "custom_partner_field",
                ]
            )

        self.assertIn("duplicate headers", str(context.exception).lower())
        self.assertIn("os_id", str(context.exception))
        self.assertIn("custom_partner_field", str(context.exception))

    def test_validate_headers_requires_data_column(self):
        header_map = PartnerFieldSheetParser.build_header_map(["os_id"])
        with self.assertRaises(ValueError) as context:
            PartnerFieldSheetParser.validate_headers(header_map)

        self.assertIn("at least one partner field", str(context.exception))

    def test_allowed_flattened_columns_for_worldly_schema(self):
        allowed = PartnerFieldSheetParser.allowed_flattened_columns(
            "worldly_assessment_data",
            WORLDLY_ASSESSMENT_SCHEMA,
        )

        self.assertIn(
            "worldly_assessment_data_fdm_assessment_assessment_url",
            allowed,
        )
        self.assertIn(
            "worldly_assessment_data_fem_assessment_reporting_year",
            allowed,
        )

    def test_build_column_mappings_scalar_and_flattened(self):
        data_columns = [
            "custom_partner_field",
            "worldly_assessment_data_fdm_assessment_assessment_url",
        ]
        header_map = PartnerFieldSheetParser.build_header_map(
            ["os_id"] + data_columns
        )
        PartnerFieldSheetParser.validate_headers(header_map)
        mappings, partner_fields = PartnerFieldSheetParser.build_column_mappings(
            data_columns,
            self.contributor,
        )

        self.assertEqual(
            set(partner_fields.keys()),
            {"custom_partner_field", "worldly_assessment_data"},
        )
        self.assertIsNone(
            mappings["custom_partner_field"].path_segments
        )
        self.assertEqual(
            mappings[
                "worldly_assessment_data_fdm_assessment_assessment_url"
            ].path_segments,
            ["fdm_assessment", "assessment_url"],
        )

    def test_build_column_mappings_rejects_unknown_column(self):
        with self.assertRaises(ValueError) as context:
            PartnerFieldSheetParser.build_column_mappings(
                ["unknown_partner_field"],
                self.contributor,
            )

        self.assertIn("Unknown or invalid", str(context.exception))

    def test_build_column_mappings_rejects_unauthorized_field(self):
        unauthorized_field = PartnerField.objects.create(
            name="other_partner_field",
            type=PartnerField.STRING,
            label="Other Partner Field",
        )
        with self.assertRaises(ValueError) as context:
            PartnerFieldSheetParser.build_column_mappings(
                [unauthorized_field.name],
                self.contributor,
            )

        self.assertIn("Unknown or invalid", str(context.exception))

    @patch.object(PartnerFieldSheetParser, "match_column")
    def test_build_column_mappings_reports_all_unauthorized_fields(
        self,
        mock_match_column,
    ):
        unauthorized_a = PartnerField.objects.create(
            name="unauthorized_field_a",
            type=PartnerField.STRING,
            label="Unauthorized Field A",
        )
        unauthorized_b = PartnerField.objects.create(
            name="unauthorized_field_b",
            type=PartnerField.STRING,
            label="Unauthorized Field B",
        )

        def match_side_effect(column, contributor_fields):
            if column == unauthorized_a.name:
                return ColumnMapping(
                    column_name=column,
                    partner_field=unauthorized_a,
                )
            if column == unauthorized_b.name:
                return ColumnMapping(
                    column_name=column,
                    partner_field=unauthorized_b,
                )
            return None

        mock_match_column.side_effect = match_side_effect

        with self.assertRaises(ValueError) as context:
            PartnerFieldSheetParser.build_column_mappings(
                [unauthorized_b.name, unauthorized_a.name],
                self.contributor,
            )

        message = str(context.exception)
        self.assertIn("not permitted", message)
        self.assertIn("unauthorized_field_a", message)
        self.assertIn("unauthorized_field_b", message)

    @patch.object(PartnerFieldSheetParser, "match_column")
    def test_build_column_mappings_reports_all_schema_missing_fields(
        self,
        mock_match_column,
    ):
        schema_less_a = PartnerField.objects.create(
            name="schema_less_object_a",
            type=PartnerField.OBJECT,
            label="Schema Less Object A",
        )
        schema_less_b = PartnerField.objects.create(
            name="schema_less_object_b",
            type=PartnerField.OBJECT,
            label="Schema Less Object B",
        )
        self.contributor.partner_fields.add(schema_less_a, schema_less_b)

        def match_side_effect(column, contributor_fields):
            for partner_field in (schema_less_a, schema_less_b):
                if column == f"{partner_field.name}_value":
                    return ColumnMapping(
                        column_name=column,
                        partner_field=partner_field,
                    )
            return None

        mock_match_column.side_effect = match_side_effect

        with self.assertRaises(ValueError) as context:
            PartnerFieldSheetParser.build_column_mappings(
                [
                    "schema_less_object_a_value",
                    "schema_less_object_b_value",
                ],
                self.contributor,
            )

        message = str(context.exception)
        self.assertIn("no JSON schema", message)
        self.assertIn("schema_less_object_a", message)
        self.assertIn("schema_less_object_b", message)

    def test_build_column_mappings_reports_unsupported_array_properties(self):
        array_field = PartnerField.objects.create(
            name="array_partner_field",
            type=PartnerField.OBJECT,
            label="Array Partner Field",
            json_schema={
                "type": "object",
                "properties": {
                    "scores": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "nested": {
                        "type": "object",
                        "properties": {
                            "tags": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                        },
                    },
                    "title": {"type": "string"},
                },
            },
        )
        self.contributor.partner_fields.add(array_field)

        with self.assertRaises(ValueError) as context:
            PartnerFieldSheetParser.build_column_mappings(
                ["custom_partner_field"],
                self.contributor,
            )

        message = str(context.exception)
        self.assertIn("unsupported array", message)
        self.assertIn("scores", message)
        self.assertIn("nested_tags", message)

    def test_build_column_mappings_rejects_invalid_flattened_suffix(self):
        with self.assertRaises(ValueError) as context:
            PartnerFieldSheetParser.build_column_mappings(
                ["worldly_assessment_data_invalid_leaf"],
                self.contributor,
            )

        self.assertIn("Unknown or invalid", str(context.exception))

    def test_build_patch_raw_data_builds_nested_object(self):
        mappings, _ = PartnerFieldSheetParser.build_column_mappings(
            [
                "custom_partner_field",
                "estimated_annual_energy_consumption",
                "worldly_assessment_data_fdm_assessment_assessment_url",
                "worldly_assessment_data_fdm_assessment_reporting_year",
            ],
            self.contributor,
        )
        raw_data = PartnerFieldSheetParser.build_patch_raw_data(
            {
                "os_id": self.facility.id,
                "custom_partner_field": "partner value",
                "estimated_annual_energy_consumption": "1500",
                "worldly_assessment_data_fdm_assessment_assessment_url": (
                    "https://example.com/report"
                ),
                "worldly_assessment_data_fdm_assessment_reporting_year": "2024",
            },
            mappings,
        )

        self.assertEqual(raw_data["custom_partner_field"], "partner value")
        self.assertEqual(raw_data["estimated_annual_energy_consumption"], 1500)
        self.assertEqual(
            raw_data["worldly_assessment_data"],
            {
                "fdm_assessment": {
                    "assessment_url": "https://example.com/report",
                    "reporting_year": 2024,
                },
            },
        )

    def test_build_patch_raw_data_requires_values(self):
        mappings, _ = PartnerFieldSheetParser.build_column_mappings(
            ["custom_partner_field"],
            self.contributor,
        )
        with self.assertRaises(ValueError) as context:
            PartnerFieldSheetParser.build_patch_raw_data(
                {
                    "os_id": self.facility.id,
                    "custom_partner_field": "",
                },
                mappings,
            )

        self.assertIn("No partner field values provided", str(context.exception))

    def test_build_patch_raw_data_reports_all_parse_errors(self):
        mappings, _ = PartnerFieldSheetParser.build_column_mappings(
            [
                "estimated_annual_energy_consumption",
                "estimated_emissions_activity",
            ],
            self.contributor,
        )
        with self.assertRaises(ValueError) as context:
            PartnerFieldSheetParser.build_patch_raw_data(
                {
                    "os_id": self.facility.id,
                    "estimated_annual_energy_consumption": "not-an-int",
                    "estimated_emissions_activity": "not-a-float",
                },
                mappings,
            )

        message = str(context.exception)
        self.assertIn("estimated_annual_energy_consumption", message)
        self.assertIn("estimated_emissions_activity", message)

    def test_format_api_errors(self):
        formatted = PartnerPatchModerationEventCreator.format_api_errors(
            {
                "detail": "The request body is invalid.",
                "errors": [
                    {
                        "field": "worldly_assessment_data.fdm_assessment.age",
                        "detail": "must be integer",
                    }
                ],
            }
        )

        self.assertIn("The request body is invalid.", formatted)
        self.assertIn("must be integer", formatted)

    @patch("api.geocoding.requests.get")
    def test_create_partner_patch_moderation_event_with_flattened_columns(
        self,
        mock_get,
    ):
        mock_get.return_value = Mock(ok=True, status_code=status.HTTP_200_OK)
        mock_get.return_value.json.return_value = geocoding_data

        mappings, _ = PartnerFieldSheetParser.build_column_mappings(
            [
                "custom_partner_field",
                "estimated_annual_energy_consumption",
                "worldly_assessment_data_fdm_assessment_assessment_url",
                "worldly_assessment_data_fdm_assessment_reporting_year",
            ],
            self.contributor,
        )
        creator = PartnerPatchModerationEventCreator(
            ModerationEventCreator(LocationContribution())
        )
        moderation_id = creator.create(
            self.contributor,
            {
                "os_id": self.facility.id,
                "custom_partner_field": "partner value",
                "estimated_annual_energy_consumption": "1500",
                "worldly_assessment_data_fdm_assessment_assessment_url": (
                    "https://example.com/report"
                ),
                "worldly_assessment_data_fdm_assessment_reporting_year": "2024",
            },
            mappings,
        )

        self.assertTrue(moderation_id)

    def test_create_partner_patch_moderation_event_unknown_os_id(self):
        mappings, _ = PartnerFieldSheetParser.build_column_mappings(
            ["custom_partner_field"],
            self.contributor,
        )
        creator = PartnerPatchModerationEventCreator(
            ModerationEventCreator(LocationContribution())
        )
        with self.assertRaises(ValueError) as context:
            creator.create(
                self.contributor,
                {
                    "os_id": "US0000000UNKNOWN",
                    "custom_partner_field": "partner value",
                },
                mappings,
            )

        self.assertIn("was not found", str(context.exception))

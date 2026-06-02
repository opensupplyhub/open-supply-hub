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
    PartnerFieldSheetParser,
    PartnerPatchModerationEventCreator,
)
from api.tests.test_data import geocoding_data


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
        self.object_field = PartnerField.objects.create(
            name="schema_field",
            type=PartnerField.OBJECT,
            label="Schema Field",
            json_schema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "age": {"type": "integer"},
                },
                "required": ["name", "age"],
            },
        )
        self.contributor.partner_fields.add(
            self.string_field,
            self.int_field,
            self.float_field,
            self.object_field,
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

    def test_validate_partner_columns_preflight_success(self):
        partner_fields = PartnerFieldSheetParser.validate_preflight(
            [
                "os_id",
                "custom_partner_field",
                "schema_field",
            ],
            self.contributor,
        )

        self.assertEqual(
            set(partner_fields.keys()),
            {"custom_partner_field", "schema_field"},
        )

    def test_validate_partner_columns_preflight_requires_partner_field(self):
        with self.assertRaises(ValueError) as context:
            PartnerFieldSheetParser.validate_preflight(
                ["os_id"],
                self.contributor,
            )

        self.assertIn("at least one partner field", str(context.exception))

    def test_validate_partner_columns_preflight_rejects_unknown_field(self):
        with self.assertRaises(ValueError) as context:
            PartnerFieldSheetParser.validate_preflight(
                ["os_id", "unknown_partner_field"],
                self.contributor,
            )

        self.assertIn(
            "Unknown or inactive partner field",
            str(context.exception),
        )

    def test_validate_partner_columns_preflight_rejects_unauthorized_field(
        self,
    ):
        unauthorized_field = PartnerField.objects.create(
            name="other_partner_field",
            type=PartnerField.STRING,
            label="Other Partner Field",
        )
        with self.assertRaises(ValueError) as context:
            PartnerFieldSheetParser.validate_preflight(
                ["os_id", unauthorized_field.name],
                self.contributor,
            )

        self.assertIn("not permitted", str(context.exception))

    def test_is_cell_empty(self):
        self.assertTrue(PartnerFieldSheetParser.is_cell_empty(None))
        self.assertTrue(PartnerFieldSheetParser.is_cell_empty(""))
        self.assertTrue(PartnerFieldSheetParser.is_cell_empty("   "))
        self.assertFalse(PartnerFieldSheetParser.is_cell_empty(0))
        self.assertFalse(PartnerFieldSheetParser.is_cell_empty("value"))

    def test_parse_cell_value_for_each_type(self):
        self.assertEqual(
            PartnerFieldSheetParser.parse_cell_value(
                " hello ",
                self.string_field,
            ),
            "hello",
        )
        self.assertEqual(
            PartnerFieldSheetParser.parse_cell_value("42", self.int_field),
            42,
        )
        self.assertEqual(
            PartnerFieldSheetParser.parse_cell_value(42, self.int_field),
            42,
        )
        self.assertEqual(
            PartnerFieldSheetParser.parse_cell_value("42.5", self.float_field),
            42.5,
        )
        self.assertEqual(
            PartnerFieldSheetParser.parse_cell_value(
                '{"name": "John", "age": 30}',
                self.object_field,
            ),
            {"name": "John", "age": 30},
        )

    def test_parse_cell_value_rejects_invalid_json(self):
        with self.assertRaises(ValueError) as context:
            PartnerFieldSheetParser.parse_cell_value(
                "{bad json}",
                self.object_field,
            )

        self.assertIn("Invalid JSON", str(context.exception))

    def test_build_partner_patch_raw_data_skips_empty_cells(self):
        raw_data = PartnerFieldSheetParser.build_patch_raw_data(
            {
                "os_id": self.facility.id,
                "custom_partner_field": "value",
                "schema_field": "",
            },
            {
                "custom_partner_field": self.string_field,
                "schema_field": self.object_field,
            },
        )

        self.assertEqual(raw_data, {"custom_partner_field": "value"})

    def test_build_partner_patch_raw_data_requires_values(self):
        with self.assertRaises(ValueError) as context:
            PartnerFieldSheetParser.build_patch_raw_data(
                {
                    "os_id": self.facility.id,
                    "custom_partner_field": "",
                },
                {"custom_partner_field": self.string_field},
            )

        self.assertIn(
            "No partner field values provided",
            str(context.exception),
        )

    def test_format_api_errors(self):
        formatted = PartnerPatchModerationEventCreator.format_api_errors(
            {
                "detail": "The request body is invalid.",
                "errors": [
                    {
                        "field": "schema_field.age",
                        "detail": "must be integer",
                    }
                ],
            }
        )

        self.assertIn("The request body is invalid.", formatted)
        self.assertIn("schema_field.age: must be integer", formatted)

    @patch("api.geocoding.requests.get")
    def test_create_partner_patch_moderation_event_success(self, mock_get):
        mock_get.return_value = Mock(ok=True, status_code=status.HTTP_200_OK)
        mock_get.return_value.json.return_value = geocoding_data

        creator = PartnerPatchModerationEventCreator(
            ModerationEventCreator(LocationContribution())
        )
        moderation_id = creator.create(
            self.contributor,
            {
                "os_id": self.facility.id,
                "custom_partner_field": "partner value",
                "estimated_annual_energy_consumption": "1500",
                "schema_field": json.dumps(
                    {"name": "John Doe", "age": 30}
                ),
            },
            {
                "custom_partner_field": self.string_field,
                "estimated_annual_energy_consumption": self.int_field,
                "schema_field": self.object_field,
            },
        )

        self.assertTrue(moderation_id)

    def test_create_partner_patch_moderation_event_unknown_os_id(self):
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
                {"custom_partner_field": self.string_field},
            )

        self.assertIn("was not found", str(context.exception))

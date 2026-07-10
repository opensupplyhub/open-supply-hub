from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase

from api.models.contributor.contributor import Contributor
from api.models.extended_field import ExtendedField
from api.models.partner_field import PartnerField
from api.models.user import User


class StripUnknownPartnerFieldKeysCommandTest(TestCase):
    def setUp(self):
        user = User.objects.create(email="strip@example.com")
        self.contributor = Contributor.objects.create(
            admin=user,
            name="Strip Contributor",
            description="",
            website="",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )
        self.partner_field = PartnerField.objects.create(
            name="rsc_grievance_mechanism",
            type=PartnerField.OBJECT,
            json_schema={
                "type": "object",
                "properties": {
                    "status": {"type": "string"},
                    "coverage": {"type": "string"},
                },
            },
        )

    def _create_extended_field(self, raw_values):
        return ExtendedField.objects.create(
            contributor=self.contributor,
            field_name="rsc_grievance_mechanism",
            value={"raw_values": raw_values},
        )

    @patch(
        "api.management.commands.strip_unknown_partner_field_keys."
        "index_facilities_new"
    )
    def test_strips_undeclared_keys(self, index_mock):
        field = self._create_extended_field(
            {
                "status": "Active",
                "coverage": "All workers",
                "internal_ID": "SECRET-123",
            }
        )

        call_command(
            "strip_unknown_partner_field_keys",
            "--no-reindex",
            stdout=StringIO(),
        )

        field.refresh_from_db()
        self.assertEqual(
            field.value["raw_values"],
            {"status": "Active", "coverage": "All workers"},
        )
        index_mock.assert_not_called()

    @patch(
        "api.management.commands.strip_unknown_partner_field_keys."
        "index_facilities_new"
    )
    def test_dry_run_does_not_modify(self, index_mock):
        raw_values = {"status": "Active", "internal_ID": "SECRET"}
        field = self._create_extended_field(dict(raw_values))

        call_command(
            "strip_unknown_partner_field_keys",
            "--dry-run",
            stdout=StringIO(),
        )

        field.refresh_from_db()
        self.assertEqual(field.value["raw_values"], raw_values)
        index_mock.assert_not_called()

    @patch(
        "api.management.commands.strip_unknown_partner_field_keys."
        "index_facilities_new"
    )
    def test_leaves_clean_records_untouched(self, index_mock):
        raw_values = {"status": "Active", "coverage": "All workers"}
        field = self._create_extended_field(dict(raw_values))

        call_command(
            "strip_unknown_partner_field_keys",
            "--no-reindex",
            stdout=StringIO(),
        )

        field.refresh_from_db()
        self.assertEqual(field.value["raw_values"], raw_values)

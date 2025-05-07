from contricleaner.lib.serializers.row_serializers.\
    row_parent_company_os_id_serializer import RowParentCompanyOSIDSerializer
from contricleaner.tests.os_id_lookup_mock import OSIDLookupMock
from django.test import TestCase


class RowParentCompanyOSIDSerializerTest(TestCase):
    def setUp(self):
        split_pattern = r', |,|\|'
        self.serializer = RowParentCompanyOSIDSerializer(
            OSIDLookupMock(),
            split_pattern
        )
        self.current = {"errors": []}

    def test_no_parent_company_os_id(self):
        empty_row = {}
        result = self.serializer.validate(empty_row, self.current.copy())

        self.assertEqual(result, self.current)
        self.assertEqual(result["errors"], [])

    def test_invalid_type_parent_company_os_id(self):
        invalid_row = {
            "parent_company_os_id": 123,
        }
        result = self.serializer.validate(invalid_row, self.current.copy())

        errors = result['errors']
        self.assertEqual(len(errors), 1)

        err = errors[0]
        self.assertIsNotNone(err)
        self.assertEqual(err['type'], 'ValueError')
        self.assertIn(
            'Expected value for parent_company_os_id to be '
            'a string or list but got int.',
            err['message'],
        )

    def test_invalid_format_parent_company_os_id(self):
        invalid_os_id = "US2025125QGXB8"
        invalid_row = {
            "parent_company_os_id": invalid_os_id,
        }
        result = self.serializer.validate(invalid_row, self.current.copy())

        self.assertEqual(len(result["errors"]), 1)
        self.assertEqual(
            result["errors"][0]["message"],
            'Expected value for parent_company_os_id should '
            f'match OS ID format but got {invalid_os_id}',
        )
        self.assertEqual(result["errors"][0]["type"], "ValidationError")

    def test_invalid_ammount_parent_company_os_id(self):
        invalid_row = {
            "parent_company_os_id": [
                "US2025125QGXB1G",
                "US2025125QGXB2G",
                "US2025125QGXB3G",
                "US2025125QGXB4G",
                "US2025125QGXB5G",
                "US2025125QGXB6G",
                "US2025125QGXB7G",
                "US2025125QGXB8G",
                "US2025125QGXB9G",
                "US2025125QGXB0G",
                "US2025125QGXB1G",
                "US2025125QGXB2G",
                "US2025125QGXB3G",
                "US2025125QGXB4G",
                "US2025125QGXB5G",
                "US2025125QGXB6G",
                "US2025125QGXB7G",
                "US2025125QGXB8G",
                "US2025125QGXB9G",
                "US2025125QGXB0G",
                "US2025125QGXB1G"
            ],
        }

        result = self.serializer.validate(invalid_row, self.current.copy())

        self.assertEqual(len(result["errors"]), 1)
        self.assertEqual(
            result["errors"][0]["message"],
            'You may submit a maximum of 20 '
            'parent_company_os_id, not 21.',
        )
        self.assertEqual(result["errors"][0]["type"], "ValidationError")

    def test_not_exist_parent_company_os_id(self):
        wrong_os_id = "XY2025125QGXB8G"
        row = {
            "parent_company_os_id": wrong_os_id,
        }
        result = self.serializer.validate(row, self.current.copy())

        self.assertEqual(len(result["errors"]), 1)
        self.assertEqual(
            result["errors"][0]["message"],
            f'The OS ID {wrong_os_id} for parent_company_os_id '
            'does not related to any production location.',
        )
        self.assertEqual(result["errors"][0]["type"], "ValidationError")

    def test_valid_parent_company_os_id(self):
        row = {
            "parent_company_os_id": "US2025125QGXB8G",
        }
        result = self.serializer.validate(row, self.current.copy())

        self.assertEqual(len(result["errors"]), 0)
        self.assertEqual(
            result["parent_company_os_id"],
            ["US2025125QGXB8G"]
        )

from contricleaner.lib.serializers.row_serializers.\
    row_additional_ids_serializer import RowAdditionalIdsSerializer

from django.test import TestCase


class RowAdditionalIdsSerializerTest(TestCase):
    def setUp(self):
        self.serializer = RowAdditionalIdsSerializer()
        self.current = {"errors": []}

    def test_no_additional_ids(self):
        empty_row = {}
        result = self.serializer.validate(empty_row, self.current.copy())

        self.assertEqual(result, self.current)
        self.assertEqual(result["errors"], [])

    def test_additional_ids_value_not_string(self):
        invalid_row = {
            "duns_id": 12345678,
            "lei_id": ["123456789012345678901234"],
            "rba_id": {},
        }
        result = self.serializer.validate(invalid_row, self.current.copy())

        errors = result['errors']
        self.assertEqual(len(errors), 3)

        errors_by_field = {err['field']: err for err in errors}

        duns_err = errors_by_field.get('duns_id')
        self.assertIsNotNone(duns_err)
        self.assertEqual(duns_err['type'], 'ValueError')
        self.assertIn(
            'Expected value for duns_id to be a string but got int.',
            duns_err['message'],
        )

        lei_err = errors_by_field.get('lei_id')
        self.assertIsNotNone(lei_err)
        self.assertEqual(lei_err['type'], 'ValueError')
        self.assertIn(
            'Expected value for lei_id to be a string but got list.',
            lei_err['message'],
        )

        rba_err = errors_by_field.get('rba_id')
        self.assertIsNotNone(rba_err)
        self.assertEqual(rba_err['type'], 'ValueError')
        self.assertIn(
            'Expected value for rba_id to be a string but got dict.',
            rba_err['message'],
        )

    def test_invalid_duns_id(self):
        invalid_row = {"duns_id": "12345678"}
        result = self.serializer.validate(invalid_row, self.current.copy())

        self.assertEqual(len(result["errors"]), 1)
        self.assertEqual(
            result["errors"][0]["message"],
            "Invalid `duns_id`: 12345678. It should be a 9-digit number.",
        )
        self.assertEqual(result["errors"][0]["field"], "duns_id")
        self.assertEqual(result["errors"][0]["type"], "ValueError")

    def test_invalid_lei_id(self):
        invalid_row = {"lei_id": "123456789012345678901234"}

        result = self.serializer.validate(invalid_row, self.current.copy())

        self.assertEqual(len(result["errors"]), 1)
        self.assertEqual(
            result["errors"][0]["message"],
            "Invalid `lei_id`: 123456789012345678901234. It should be a "
            "20-character string with 18 alphanumeric characters followed "
            "by 2 digits.",
        )
        self.assertEqual(result["errors"][0]["field"], "lei_id")
        self.assertEqual(result["errors"][0]["type"], "ValueError")

    def test_invalid_rba_id(self):
        invalid_row = {"rba_id": "x" * 256}

        result = self.serializer.validate(invalid_row, self.current.copy())

        self.assertEqual(len(result["errors"]), 1)
        self.assertEqual(
            result["errors"][0]["message"],
            f"Invalid `rba_id`: {'x' * 256}. It should be a string with a "
            "maximum length of 255 characters.",
        )
        self.assertEqual(result["errors"][0]["field"], "rba_id")
        self.assertEqual(result["errors"][0]["type"], "ValueError")

    def test_valid_additional_ids(self):
        valid_row = {
            "duns_id": "150448382",
            "lei_id": "5299040T83B49AURSD55",
            "rba_id": "RBA-12345678",
        }

        result = self.serializer.validate(valid_row, self.current.copy())

        self.assertEqual(result["duns_id"], "150448382")
        self.assertEqual(result["lei_id"], "5299040T83B49AURSD55")
        self.assertEqual(result["rba_id"], "RBA-12345678")
        self.assertEqual(result["errors"], [])

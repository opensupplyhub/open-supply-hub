from contricleaner.lib.serializers.row_serializers.\
    row_additional_ids_serializer import RowAdditionalIdsSerializer
from django.test import TestCase


class RowAdditionalIdsSerializerTest(TestCase):
    def setUp(self):
        self.serializer = RowAdditionalIdsSerializer()
        self.current = {"errors": []}

    def test_none_additional_ids(self):
        empty_row = {}
        result = self.serializer.validate(empty_row, self.current.copy())

        self.assertEqual(result, self.current)
        self.assertEqual(result["errors"], [])

    def test_empty_additional_ids_dict(self):
        empty_row = {"additional_ids": {}}
        result = self.serializer.validate(empty_row, self.current.copy())

        self.assertEqual(result, self.current)
        self.assertEqual(result["errors"], [])

    def test_additional_ids_not_dict(self):
        invalid_row = {"additional_ids": "invalid_value"}
        result = self.serializer.validate(invalid_row, self.current.copy())

        self.assertEqual(len(result["errors"]), 1)
        self.assertEqual(
            result["errors"][0]["message"],
            "Expected value for additional_ids to be a dict but "
            "got invalid_value.",
        )
        self.assertEqual(result["errors"][0]["field"], "additional_ids")
        self.assertEqual(result["errors"][0]["type"], "ValueError")

    def test_additional_ids_key_not_in_allowed_keys(self):
        invalid_row = {"additional_ids": {"invalid_key": "value"}}
        result = self.serializer.validate(invalid_row, self.current.copy())

        self.assertEqual(len(result["errors"]), 1)
        self.assertEqual(
            result["errors"][0]["message"],
            "Unexpected key invalid_key in additional_ids. The allowed keys "
            "are: duns_id, lei_id, rba_id.",
        )
        self.assertEqual(result["errors"][0]["field"], "additional_ids")
        self.assertEqual(result["errors"][0]["type"], "KeyError")

    def test_additional_ids_value_not_string(self):
        invalid_row = {
            "additional_ids": {
                "duns_id": 12345678,
                "lei_id": ["123456789012345678901234"],
                "rba_id": {},
            }
        }
        result = self.serializer.validate(invalid_row, self.current.copy())

        self.assertEqual(len(result["errors"]), 3)
        self.assertEqual(
            result["errors"][0]["message"],
            "Expected value for duns_id to be a string but got int.",
        )
        self.assertEqual(result["errors"][0]["field"], "additional_ids")
        self.assertEqual(result["errors"][0]["type"], "ValueError")
        self.assertEqual(
            result["errors"][1]["message"],
            "Expected value for lei_id to be a string but got list.",
        )
        self.assertEqual(result["errors"][1]["field"], "additional_ids")
        self.assertEqual(result["errors"][1]["type"], "ValueError")
        self.assertEqual(
            result["errors"][2]["message"],
            "Expected value for rba_id to be a string but got dict.",
        )
        self.assertEqual(result["errors"][2]["field"], "additional_ids")
        self.assertEqual(result["errors"][2]["type"], "ValueError")

    def test_invalid_duns_id(self):
        invalid_row = {"additional_ids": {"duns_id": "12345678"}}
        result = self.serializer.validate(invalid_row, self.current.copy())

        self.assertEqual(len(result["errors"]), 1)
        self.assertEqual(
            result["errors"][0]["message"],
            "Invalid `duns_id`: 12345678. It should be a 9-digit number.",
        )
        self.assertEqual(result["errors"][0]["field"], "additional_ids")
        self.assertEqual(result["errors"][0]["type"], "ValueError")

    def test_invalid_lei_id(self):
        invalid_row = {
            "additional_ids": {"lei_id": "123456789012345678901234"}
        }
        result = self.serializer.validate(invalid_row, self.current.copy())

        self.assertEqual(len(result["errors"]), 1)
        self.assertEqual(
            result["errors"][0]["message"],
            "Invalid `lei_id`: 123456789012345678901234. It should be a "
            "20-character string with 18 alphanumeric characters followed "
            "by 2 digits.",
        )
        self.assertEqual(result["errors"][0]["field"], "additional_ids")
        self.assertEqual(result["errors"][0]["type"], "ValueError")

    def test_invalid_rba_id(self):
        invalid_row = {
            "additional_ids": {
                "rba_id": "x" * 256,
            }
        }
        result = self.serializer.validate(invalid_row, self.current.copy())

        self.assertEqual(len(result["errors"]), 1)
        self.assertEqual(
            result["errors"][0]["message"],
            f"Invalid `rba_id`: {'x' * 256}. It should be a string with a "
            "maximum length of 255 characters.",
        )
        self.assertEqual(result["errors"][0]["field"], "additional_ids")
        self.assertEqual(result["errors"][0]["type"], "ValueError")

    def test_valid_additional_ids(self):
        valid_row = {
            "additional_ids": {
                "duns_id": "150448382",
                "lei_id": "5299040T83B49AURSD55",
                "rba_id": "RBA-12345678",
            }
        }
        result = self.serializer.validate(valid_row, self.current.copy())

        self.assertEqual(result["duns_id"], "150448382")
        self.assertEqual(result["lei_id"], "5299040T83B49AURSD55")
        self.assertEqual(result["rba_id"], "RBA-12345678")
        self.assertEqual(result["errors"], [])

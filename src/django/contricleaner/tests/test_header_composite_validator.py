
import unittest

from contricleaner.lib.header_validators.header_composite_validator import (
    HeaderCompositeValidator
)


class HeaderCompositeValidatorTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_get_validated_header(self):
        validator = HeaderCompositeValidator()
        res = validator.get_validated_header(["Name", 'name', "Age", "Email"])
        self.assertEqual(res.errors, [
            {
                "message": "'name' or 'address' are missing",
                "type": "Error",
            },
            {'message': 'One or more fields are duplicated', 'type': 'Error'}
        ])
        self.assertEqual(res.raw_header, ["Name", 'name', "Age", "Email"])
        self.assertEqual(res.fields, {"name", "age", "email"})
        self.assertEqual(res.non_standard_fields, {"age", "email"})

        
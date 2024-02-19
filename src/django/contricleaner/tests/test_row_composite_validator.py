
import unittest

from contricleaner.lib.row_validators.row_composite_validator import (
    RowCompositeValidator
)


class RowCompositeValidatorTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_get_validated_row(self):
        validator = RowCompositeValidator()
        res = validator.get_validated_row({'name': 'test'})

        
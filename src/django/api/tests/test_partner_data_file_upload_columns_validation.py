from django.core.exceptions import ValidationError
from django.test import SimpleTestCase

from api.models.partner_data_file_upload import validate_columns_to_process


class PartnerDataFileUploadColumnsValidationTest(SimpleTestCase):
    def test_accepts_valid_comma_separated_snake_case_columns(self):
        self.assertEqual(
            validate_columns_to_process(
                "os_id,name,address,country,sector"
            ),
            "os_id,name,address,country,sector",
        )

    def test_trims_whitespace_around_commas(self):
        self.assertEqual(
            validate_columns_to_process(" os_id , name , address "),
            "os_id,name,address",
        )

    def test_rejects_empty_value(self):
        with self.assertRaises(ValidationError) as context:
            validate_columns_to_process("")

        self.assertIn("cannot be empty", str(context.exception))

    def test_rejects_empty_entries_from_trailing_comma(self):
        with self.assertRaises(ValidationError) as context:
            validate_columns_to_process("os_id,name,")

        self.assertIn("without empty entries", str(context.exception))

    def test_rejects_empty_entries_from_double_comma(self):
        with self.assertRaises(ValidationError) as context:
            validate_columns_to_process("os_id,,name")

        self.assertIn("without empty entries", str(context.exception))

    def test_rejects_uppercase_values(self):
        with self.assertRaises(ValidationError) as context:
            validate_columns_to_process("OS_ID,name")

        self.assertIn('Invalid column name "OS_ID"', str(context.exception))

    def test_rejects_values_with_spaces(self):
        with self.assertRaises(ValidationError) as context:
            validate_columns_to_process("os id,name")

        self.assertIn('Invalid column name "os id"', str(context.exception))

    def test_rejects_values_with_hyphens(self):
        with self.assertRaises(ValidationError) as context:
            validate_columns_to_process("os-id,name")

        self.assertIn('Invalid column name "os-id"', str(context.exception))

    def test_rejects_values_starting_with_number(self):
        with self.assertRaises(ValidationError) as context:
            validate_columns_to_process("1_name,name")

        self.assertIn('Invalid column name "1_name"', str(context.exception))

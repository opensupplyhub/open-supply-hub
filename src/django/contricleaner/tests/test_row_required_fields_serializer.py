import unittest

from contricleaner.lib.serializers.row_serializers \
    .row_required_fields_serializer \
    import RowRequiredFieldsSerializer


class RowRequiredFieldsSerializerTest(unittest.TestCase):
    def setUp(self):
        self.serializer = RowRequiredFieldsSerializer()
        self.current = {"errors": []}

    def test_validate_required_fields(self):
        headers_one = ["name",
                       "address",
                       "country",
                       "sector"]

        res_one = self.serializer.validate(headers_one, self.current)

        self.assertEqual(len(res_one["errors"]), 0)

        headers_two = ["name",
                       "country",
                       "sector"]

        res_two = self.serializer.validate(headers_two, self.current)

        self.assertEqual(len(res_two["errors"]), 1)

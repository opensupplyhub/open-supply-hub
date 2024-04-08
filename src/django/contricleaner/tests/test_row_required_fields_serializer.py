from django.test import TestCase

from contricleaner.lib.serializers.row_serializers \
    .row_required_fields_serializer \
    import RowRequiredFieldsSerializer


class RowRequiredFieldsSerializerTest(TestCase):
    def setUp(self):
        self.serializer = RowRequiredFieldsSerializer()
        self.current = {"errors": []}

    def test_validate_required_fields(self):
        facility_source_one = {
            "country": "United States",
            "name": "Pants Hut",
            "address": "123 Main St, Anywhereville, PA",
            "sector": "Apparel",
            "extra_1": "Extra data",
        }

        res_one = self.serializer.validate(facility_source_one, self.current)

        self.assertEqual(len(res_one["errors"]), 0)

        facility_source_two = {
            "country": "United States",
            "name": "Pants Hut",
            "sector": "Apparel",
            "extra_1": "Extra data",
        }

        res_two = self.serializer.validate(facility_source_two, self.current)

        self.assertEqual(len(res_two["errors"]), 1)

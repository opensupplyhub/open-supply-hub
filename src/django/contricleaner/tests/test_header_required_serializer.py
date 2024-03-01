import unittest

from contricleaner.lib.serializers.header_serializers \
    .header_required_serializer \
        import HeaderRequiredSerializer


class HeaderRequiredSerializerTest(unittest.TestCase):
    def setUp(self):
        self.serializer = HeaderRequiredSerializer()
        self.current = {"errors": []}

    def test_validate_required_headers(self):
        headers_one = ["name",
                       "address",
                       "country",
                       "sector"]

        res_one = self.serializer.validate(headers_one, self.current)

        self.assertCountEqual(len(res_one["errors"]), 0)

        headers_two = ["name",
                       "country",
                       "sector"]

        res_two = self.serializer.validate(headers_two, self.current)

        self.assertCountEqual(len(res_two["errors"]), 1)

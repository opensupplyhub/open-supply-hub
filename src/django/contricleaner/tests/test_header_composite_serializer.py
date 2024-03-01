import unittest

from contricleaner.lib.dto.header_dto import HeaderDTO
from contricleaner.lib.serializers.header_serializers \
    .header_composite_serializer \
    import HeaderCompositeSerializer


class HeaderCompositeValidatorTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_get_validated_headers(self):
        validator = HeaderCompositeSerializer()
        headers = ["name",
                   "address",
                   "country",
                   "sector"]

        res = validator.get_validated_headers(headers)

        expected = HeaderDTO(
            headers=headers,
            errors=[],
        )

        self.assertHeadersEqual(res, expected)

    def assertHeadersEqual(self, res, expected):
        self.assertEqual(res.errors, expected.errors)
        self.assertEqual(res.headers, expected.headers)

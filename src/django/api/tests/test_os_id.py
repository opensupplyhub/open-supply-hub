from api.os_id import make_os_id, validate_os_id

from django.test import TestCase


class OsIdTest(TestCase):
    def test_make_and_validate_os_id(self):
        id = make_os_id("US")
        validate_os_id(id)
        self.assertEqual(id[:2], "US")

    def test_id_too_long(self):
        self.assertRaises(ValueError, validate_os_id, "US2019070KTWK4x")

    def test_invalid_checksum(self):
        self.assertRaises(ValueError, validate_os_id, "USX019070KTWK4")

    def test_invalid_country(self):
        self.assertRaises(ValueError, make_os_id, "99")

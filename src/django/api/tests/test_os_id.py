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

    def test_character_outside_base32_returns_false_when_not_raising(self):
        """
        Crockford base 32 omits I, L, O and U. With raise_on_invalid False
        the contract is to return False, so one of those must not escape
        as a bare ValueError from the checksum.
        """
        for bad in (
            "XX0000000BADID1",  # I
            "XX0000000BADLD1",  # L
            "XX0000000BADOD1",  # O
            "XX0000000BADUD1",  # U
        ):
            with self.subTest(os_id=bad):
                self.assertFalse(
                    validate_os_id(bad, raise_on_invalid=False)
                )

    def test_character_outside_base32_raises_when_asked(self):
        self.assertRaises(
            ValueError, validate_os_id, "XX0000000BADID1"
        )

    def test_country_code_may_contain_omitted_letters(self):
        """
        The guard applies from position two onward. I, L, O and U are
        legitimate in a country code, so IN, IL and LU must still work.
        """
        for country in ("IN", "IL", "LU", "US"):
            with self.subTest(country=country):
                validate_os_id(make_os_id(country))

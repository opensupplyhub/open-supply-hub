from api.helpers.attachment_download import build_content_disposition

from django.test import TestCase


class BuildContentDispositionTest(TestCase):
    '''
    OSDEV-3600: a display name carrying Turkish or CJK characters was
    emitted as a bare `filename="..."`, which S3 rejected with
    `InvalidArgument: Header value cannot be represented using
    ISO-8859-1`.
    '''

    # Dotless i and the cedilla letters are the live failure case.
    TURKISH_NAME = 'işyeri-açma-ve-çalıştırma-ruhsatı.pdf'

    def assert_header_safe(self, disposition):
        '''
        The whole value must survive the ISO-8859-1 encoding that HTTP
        header serialization applies. This is the regression guard.
        '''
        disposition.encode('latin-1')
        self.assertTrue(disposition.isascii())

    def test_ascii_name_is_unchanged_in_the_plain_form(self):
        disposition = build_content_disposition('business-license.pdf')

        self.assertIn('filename="business-license.pdf"', disposition)
        self.assert_header_safe(disposition)

    def test_turkish_name_is_header_safe(self):
        disposition = build_content_disposition(self.TURKISH_NAME)

        self.assert_header_safe(disposition)

    def test_turkish_name_preserved_exactly_in_rfc_5987_form(self):
        disposition = build_content_disposition(self.TURKISH_NAME)

        # Percent-decoding filename* must give back the original name,
        # byte for byte.
        from urllib.parse import unquote

        _, _, encoded = disposition.partition("filename*=UTF-8''")
        self.assertEqual(self.TURKISH_NAME, unquote(encoded))

    def test_turkish_name_folds_to_readable_ascii_fallback(self):
        disposition = build_content_disposition(self.TURKISH_NAME)

        # Dotless i and s-cedilla fold rather than vanish, so the
        # fallback stays legible.
        self.assertIn(
            'filename="isyeri-acma-ve-calistirma-ruhsati.pdf"',
            disposition,
        )

    def test_cjk_name_keeps_its_extension_in_the_fallback(self):
        disposition = build_content_disposition('营业执照.pdf')

        # Nothing of the stem survives ASCII folding, but the extension
        # must, so the fallback still opens in the right application.
        self.assertIn('filename="attachment.pdf"', disposition)
        self.assert_header_safe(disposition)

    def test_cjk_name_preserved_in_rfc_5987_form(self):
        from urllib.parse import unquote

        disposition = build_content_disposition('营业执照.pdf')

        _, _, encoded = disposition.partition("filename*=UTF-8''")
        self.assertEqual('营业执照.pdf', unquote(encoded))

    def test_both_forms_are_emitted(self):
        disposition = build_content_disposition(self.TURKISH_NAME)

        self.assertTrue(disposition.startswith('attachment; filename="'))
        self.assertIn("filename*=UTF-8''", disposition)

    def test_quotes_are_stripped(self):
        disposition = build_content_disposition('a"b".pdf')

        self.assertIn('filename="ab.pdf"', disposition)
        self.assert_header_safe(disposition)

    def test_path_separators_are_stripped(self):
        disposition = build_content_disposition('../../etc/passwd.pdf')

        self.assertNotIn('/', disposition)
        self.assertIn('filename="....etcpasswd.pdf"', disposition)

    def test_name_without_extension_is_handled(self):
        disposition = build_content_disposition('营业执照')

        self.assertIn('filename="attachment"', disposition)
        self.assert_header_safe(disposition)

    def test_empty_name_falls_back(self):
        disposition = build_content_disposition('')

        self.assertIn('filename="attachment"', disposition)
        self.assert_header_safe(disposition)

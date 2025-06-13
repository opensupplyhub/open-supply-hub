from django.test import TestCase
from django.utils import timezone
from api.models import User, FacilityDownloadLimit


class FacilityDownloadLimitModelTest(TestCase):
    def setUp(self):
        self.email = "test@example.com"
        self.test_pass = "example123"
        self.user = User.objects.create(email=self.email)
        self.user.set_password(self.test_pass)
        self.user.save()

    def test_register_download(self):
        expected_free_download_records_before = 5000
        expected_free_download_records_after = 0
        expected_paid_download_records_before = 1000
        expected_paid_download_records_after = 0
        records_to_subtract = 6000

        limit = FacilityDownloadLimit.objects.create(
          user=self.user,
          paid_download_records = 1000,
        )
        self.assertEqual(
            limit.free_download_records,
            expected_free_download_records_before
        )
        self.assertEqual(
            limit.paid_download_records,
            expected_paid_download_records_before
        )

        limit.register_download(records_to_subtract)

        self.assertEqual(
            limit.free_download_records,
            expected_free_download_records_after
        )
        self.assertEqual(
            limit.paid_download_records,
            expected_paid_download_records_after
        )

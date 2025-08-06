from django.test import TestCase
from api.models import User, FacilityDownloadLimit
from api.services.facilities_download_service import FacilitiesDownloadService


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
          paid_download_records=1000
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

    def test_register_download_if_needed_with_is_same_contributor_true(self):
        """
        Test that when is_same_contributor=True,
        download limits are NOT decremented.
        """
        limit = FacilityDownloadLimit.objects.create(
            user=self.user,
            free_download_records=100,
            paid_download_records=200
        )

        initial_free = limit.free_download_records
        initial_paid = limit.paid_download_records
        records_to_subtract = 50

        FacilitiesDownloadService.register_download_if_needed(
            limit, records_to_subtract, is_same_contributor=True
        )

        limit.refresh_from_db()
        self.assertEqual(limit.free_download_records, initial_free)
        self.assertEqual(limit.paid_download_records, initial_paid)

    def test_register_download_if_needed_with_is_same_contributor_false(self):
        """
        Test that when is_same_contributor=False,
        download limits are decremented.
        """
        limit = FacilityDownloadLimit.objects.create(
            user=self.user,
            free_download_records=100,
            paid_download_records=200
        )

        initial_free = limit.free_download_records
        initial_paid = limit.paid_download_records
        records_to_subtract = 50

        FacilitiesDownloadService.register_download_if_needed(
            limit, records_to_subtract, is_same_contributor=False
        )

        limit.refresh_from_db()
        self.assertEqual(
            limit.free_download_records, initial_free - records_to_subtract
        )
        self.assertEqual(limit.paid_download_records, initial_paid)

    def test_register_download_if_needed_exceeds_free_limit(self):
        """
        Test that when records exceed free limit,
        paid records are used.
        """
        limit = FacilityDownloadLimit.objects.create(
            user=self.user,
            free_download_records=50,
            paid_download_records=200
        )

        initial_free = limit.free_download_records
        initial_paid = limit.paid_download_records
        records_to_subtract = 100  # Exceeds free limit

        FacilitiesDownloadService.register_download_if_needed(
            limit, records_to_subtract, is_same_contributor=False
        )

        limit.refresh_from_db()
        self.assertEqual(limit.free_download_records, 0)
        self.assertEqual(
            limit.paid_download_records,
            initial_paid - (records_to_subtract - initial_free)
        )

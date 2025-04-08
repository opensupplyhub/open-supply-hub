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

    def test_create_default_facility_download_limit_record(self):
        expected_time = timezone.now()
        facility_download_limit = FacilityDownloadLimit \
            .get_or_create_user_download_limit(self.user)

        # Strip seconds and microseconds
        dt1_trimmed = expected_time.replace(second=0, microsecond=0)
        dt2_trimmed = facility_download_limit.last_download_time \
            .replace(second=0, microsecond=0)

        self.assertEqual(
            dt2_trimmed,
            dt1_trimmed
        )
        self.assertEqual(
            facility_download_limit.allowed_downloads,
            10
        )
        self.assertEqual(
            facility_download_limit.download_count,
            0
        )
        self.assertEqual(
            facility_download_limit.allowed_records_number,
            1000
        )

    def test_increment_download_count(self):
        expected_count_before = 0
        expected_count_after = 1

        facility_download_limit = FacilityDownloadLimit.objects.create(
          user=self.user,
        )

        self.assertEqual(
            facility_download_limit.download_count,
            expected_count_before
        )

        facility_download_limit.increment_download_count()
        new_facility_download_limit = FacilityDownloadLimit.objects.get(
          user=self.user,
        )

        self.assertEqual(
            new_facility_download_limit.download_count,
            expected_count_after
        )

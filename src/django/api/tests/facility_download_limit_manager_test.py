from datetime import timedelta
from django.test import TestCase
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from api.models import FacilityDownloadLimit, User
from api.constants import FacilitiesDownloadSettings


class FacilityDownloadLimitManagerTest(TestCase):
    def setUp(self):
        self.manager = FacilityDownloadLimit.objects
        email_one = "one@example.com"
        email_two = "two@example.com"
        email_three = "three.free@example.com"
        email_four = "four@example.com"
        email_five = "five@example.com"
        self.user_one = User.objects.create(email=email_one)
        self.user_two = User.objects.create(email=email_two)
        self.user_three = User.objects.create(email=email_three)
        self.user_four = User.objects.create(email=email_four)
        self.user_five = User.objects.create(email=email_five)

    def test_update_expired_limits(self):
        now = timezone.now()
        one_year_ago = now - relativedelta(years=1)

        # Create a record expired for free limits
        # (updated_at older than 1 year)
        expired_free = FacilityDownloadLimit\
            .objects.create(
                user=self.user_one,
                free_download_records=100,
                paid_download_records=10,
                updated_at=one_year_ago-timedelta(days=1),
                purchase_date=now,
            )

        # Create a record NOT expired for free limits
        # (updated_at recent)
        fresh_free = FacilityDownloadLimit.objects.create(
            user=self.user_two,
            free_download_records=100,
            paid_download_records=10,
            updated_at=now,
            purchase_date=now,
        )

        # Create a record expired for paid limits
        # (purchase_date older than 1 year and
        # paid_download_records != 0)
        expired_paid = FacilityDownloadLimit.objects.create(
            user=self.user_three,
            free_download_records=100,
            paid_download_records=10,
            updated_at=now,
            purchase_date=one_year_ago-timedelta(days=1),
        )

        # Create a record NOT expired for paid limits
        # (purchase_date recent)
        fresh_paid = FacilityDownloadLimit\
            .objects.create(
                user=self.user_four,
                free_download_records=100,
                paid_download_records=10,
                updated_at=now,
                purchase_date=now,
            )

        # Create a record with purchase_date old
        # but paid_download_records=0
        # (should NOT be updated)
        expired_paid_zero = FacilityDownloadLimit\
            .objects.create(
                user=self.user_five,
                free_download_records=100,
                paid_download_records=0,
                updated_at=now,
                purchase_date=one_year_ago-timedelta(days=1),
            )

        self.manager.update_expired_limits()

        # Refresh from DB
        expired_free.refresh_from_db()
        fresh_free.refresh_from_db()
        expired_paid.refresh_from_db()
        fresh_paid.refresh_from_db()
        expired_paid_zero.refresh_from_db()

        # Assert expired free limits updated
        self.assertEqual(
            expired_free.free_download_records,
            FacilitiesDownloadSettings.FACILITIES_DOWNLOAD_LIMIT,
        )
        self.assertTrue(expired_free.updated_at > one_year_ago)

        # Assert fresh free limits unchanged
        self.assertEqual(fresh_free.free_download_records, 100)
        self.assertEqual(fresh_free.updated_at, fresh_free.updated_at)

        # Assert expired paid limits reset to 0
        self.assertEqual(expired_paid.paid_download_records, 0)

        # Assert fresh paid limits unchanged
        self.assertEqual(fresh_paid.paid_download_records, 10)

        # Assert expired paid limit with zero records remains zero
        self.assertEqual(expired_paid_zero.paid_download_records, 0)

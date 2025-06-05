from typing import Optional
from django.db import models
from django.utils import timezone
from django.db import transaction
from django.db.models import BigAutoField
from api.constants import FacilitiesDownloadSettings
# from datetime import timedelta
from datetime import datetime

class FacilityDownloadLimit(models.Model):
    """
    Stores the number of facility records allowed for free download per
    calendar year, the number of paid facility records for non-API
    users, and date of last update of free facilities records.
    """
    id = BigAutoField(
        auto_created=True,
        primary_key=True,
        serialize=False
    )
    user = models.OneToOneField(
        'User',
        null=False,
        on_delete=models.CASCADE,
        help_text='The user to whom the download limit applies.'
    )
    free_download_records = models.PositiveIntegerField(
        null=False,
        blank=False,
        default=FacilitiesDownloadSettings.FACILITIES_DOWNLOAD_LIMIT,
        help_text=('The number of facilities the user '
                   'can download per calendar year for free.')
    )
    paid_download_records = models.PositiveIntegerField(
        null=False,
        blank=False,
        default=0,
        help_text=('The number of paid facilities that the user can download.')
    )
    updated_at = models.DateTimeField(
        null=False,
        blank=False,
        auto_now=True,
        help_text='The date when the free limit was updated.'
    )

    def is_free_limit_expired(self):
        # # is one year expired
        # return timezone.now() >= self.updated_at + timedelta(days=365)
        updated_year = self.updated_at.year
        next_year_start = datetime(
            year=updated_year + 1,
            month=1,
            day=1,
            tzinfo=self.updated_at.tzinfo  # preserve timezone
        )
        return timezone.now() >= next_year_start

    def register_download(self, records_to_subtract):
        with transaction.atomic():
            self.refresh_from_db()
            if self.free_download_records >= records_to_subtract:
                self.free_download_records = self.free_download_records - records_to_subtract
            else:
                remaining_records = records_to_subtract - self.free_download_records
                self.free_download_records = 0
                self.paid_download_records -= remaining_records
            self.save()

    @staticmethod
    def get_or_create_user_download_limit(
        user
    ) -> Optional["FacilityDownloadLimit"]:
        is_api_user = not user.is_anonymous and user.has_groups

        if is_api_user or user.is_anonymous:
            # if user is an API user we don't want to impose limits
            return None

        facility_download_limit, _ = FacilityDownloadLimit \
            .objects.get_or_create(user=user)
        print('!!!', facility_download_limit.is_free_limit_expired())
        if (facility_download_limit.is_free_limit_expired()):
            facility_download_limit.free_download_records = FacilitiesDownloadSettings.FACILITIES_DOWNLOAD_LIMIT
            facility_download_limit.updated_at = timezone.now()
            facility_download_limit.save()
        return facility_download_limit

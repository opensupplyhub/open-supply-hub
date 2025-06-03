from typing import Optional
from django.db import models
from django.forms import ValidationError
from django.utils import timezone
from django.db import transaction
from django.db.models import BigAutoField, F
from api.constants import FacilitiesDownloadSettings
from datetime import datetime

def first_day_of_next_year():
    now = timezone.now()
    return datetime(year=now.year + 1, month=1, day=1, tzinfo=now.tzinfo)

class FacilityDownloadLimit(models.Model):
    """
    Stores the number of facility records allowed for free download per
    calendar year, the number of paid facility records, and the count of
    both paid and free records already downloaded by registered (non-API)
    users.
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
    free_download_records_limit = models.PositiveIntegerField(
        null=False,
        blank=False,
        default=FacilitiesDownloadSettings.FACILITIES_DOWNLOAD_LIMIT,
        help_text=('The number of facilities a user '
                   'can download per calendar year for free.')
    )
    paid_download_records_limit = models.PositiveIntegerField(
        null=False,
        blank=False,
        default=0,
        help_text=('The number of paid facilities that a user can download.')
    )
    remaining_free_records = models.PositiveIntegerField(
        null=False,
        blank=False,
        default=0,
        help_text=('The number of free facilities of the user '
                   'has remaining in the current year.'),
        verbose_name='Current remaining free records',
    )
    remaining_paid_records = models.PositiveIntegerField(
        null=False,
        blank=False,
        default=0,
        help_text=('The number of paid facilities of the user '
                   'has remaining.'),
        verbose_name='Current remaining paid records',
    )
    limit_update_date = models.DateTimeField(
        null=False,
        blank=False,
        default=first_day_of_next_year,
        help_text='The date when the free limit should be updated.'
    )

    def register_download(self):
        with transaction.atomic():
            self.refresh_from_db()
            # free_left = self.free_download_records_limit - self.free_downloaded_records
            # paid_left =  self.paid_download_records_limit !==0 ?self.paid_download_records_limit - self.paid_downloaded_records:0
            # if total_to_download <= free_left:
            #     # All from free quota
            #     self.free_download_records_limit -= free_left + paid_left
            # elif total_to_download <= (user.free_downloads_remaining + user.paid_downloads_remaining):
            #     # Use free first, then paid
            #     free_used = user.free_downloads_remaining
            #     paid_needed = total_to_download - free_used

            #     user.free_downloads_remaining = 0
            #     user.paid_downloads_remaining -= paid_needed
            # else:
            #     raise ValueError("Not enough free or paid quota to download the requested facilities.")

            # if (
            #     self.download_count >=
            #     self.allowed_downloads
            # ):
                # raise ValidationError("Concurrent limit exceeded.")
            # self.last_download_time = timezone.now()
            # self.download_count = F('download_count') + 1

            # check free records if > then save to paid
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
        # current_date = timezone.now()
        # last_download_month = facility_download_limit \
        #     .last_download_time.month
        # last_download_year = facility_download_limit \
        #     .last_download_time.year
        # if (
        #     current_date.year != last_download_year
        # ):
            # facility_download_limit.download_count = 0
            # facility_download_limit.last_download_time = timezone.now()
            # facility_download_limit.save()
        return facility_download_limit
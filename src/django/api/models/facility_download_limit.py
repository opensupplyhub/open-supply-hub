from typing import Optional
from django.db import models
from django.forms import ValidationError
from django.utils import timezone
from django.db import transaction
from django.db.models import BigAutoField, F
from api.constants import FacilitiesDownloadSettings


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
    free_downloaded_records = models.PositiveIntegerField(
        null=False,
        blank=False,
        default=0,
        help_text=('The number of free facilities a user '
                   'has already been downloaded in the current year.'),
        verbose_name='Current free downloaded records',
    )
    paid_downloaded_records = models.PositiveIntegerField(
        null=False,
        blank=False,
        default=0,
        help_text=('The number of paid facilities a user '
                   'has already been downloaded.'),
        verbose_name='Current paid downloaded records',
    )
    def increment_download_count(self):
        with transaction.atomic():
            self.refresh_from_db()
            if (
                self.download_count >=
                self.allowed_downloads
            ):
                raise ValidationError("Concurrent limit exceeded.")
            self.last_download_time = timezone.now()
            self.download_count = F('download_count') + 1
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
            .objects.get_or_create(
                user=user,
                defaults={
                    "last_download_time": timezone.now(),
                    "allowed_downloads": (
                        FacilitiesDownloadSettings.DEFAULT_ALLOWED_DOWNLOADS
                    ),
                    "download_count": 0,
                    "allowed_records_number": (
                        FacilitiesDownloadSettings.FACILITIES_DOWNLOAD_LIMIT
                    ),
                }
            )
        current_date = timezone.now()
        last_download_month = facility_download_limit \
            .last_download_time.month
        last_download_year = facility_download_limit \
            .last_download_time.year
        if (
            current_date.month != last_download_month or
            current_date.year != last_download_year
        ):
            facility_download_limit.download_count = 0
            facility_download_limit.last_download_time = timezone.now()
            facility_download_limit.save()
        return facility_download_limit
from typing import Optional
from django.db import models
from django.forms import ValidationError
from django.utils import timezone
from django.db import transaction
from django.db.models import BigAutoField, F
from django.db import models
from django.utils import timezone
from django.db.models import (
    BigAutoField,
)
from api.constants import FacilitiesDownloadSettings


class FacilityDownloadLimit(models.Model):
    """
    Stores the number of facility data downloads, the timestamp
    of the last download, and the monthly download limit for a
    registered free user.
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
    last_download_time = models.DateTimeField(
        null=False,
        blank=False,
        default=timezone.now,
        help_text='The date of the last download.'
    )
    allowed_downloads = models.PositiveIntegerField(
        null=False,
        blank=False,
        default=FacilitiesDownloadSettings.DEFAULT_ALLOWED_DOWNLOADS,
        help_text=('The number of facility data downloads a user '
                   'can make per month.')
    )
    allowed_records_number = models.PositiveIntegerField(
        null=False,
        blank=False,
        default=FacilitiesDownloadSettings.FACILITIES_DOWNLOAD_LIMIT,
        help_text=('The maximum number of facility records a user '
                   'can download in a single request.')
    )
    download_count = models.PositiveIntegerField(
        null=False,
        blank=False,
        default=0,
        help_text=('The number of facility data downloads a user '
                   'has already made in the current month.'),
        verbose_name='Current download count',
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

        current_month = timezone.now().month
        last_download_month = facility_download_limit \
            .last_download_time.month

        if current_month != last_download_month:
            facility_download_limit.download_count = 0
            facility_download_limit.last_download_time = timezone.now()

        return facility_download_limit

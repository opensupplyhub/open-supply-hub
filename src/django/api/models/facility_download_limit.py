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

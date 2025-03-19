from simple_history.models import HistoricalRecords
from django.db import models
from django.db.models import (
    BigAutoField,
)


class ApiFacilityDownloadLimit(models.Model):
    """
    Stores the number of facility data downloads, the timestamp of the last download,
    and the monthly download limit for a registered free user.
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
        null=True,
        blank=True,
        help_text='The date of the last download.'
    )
    allowed_downloads = models.PositiveIntegerField(
        null=False,
        blank=False,
        help_text=('The number of facility data downloads a user '
                   'can make per month.')
    )
    download_count = models.PositiveIntegerField(
        null=False,
        blank=False,
        help_text=('The number of facility data downloads a user '
                   'has already made in the current month.')
    )

    history = HistoricalRecords()

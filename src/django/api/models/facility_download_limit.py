from django.db import models
from django.db.models import (
    BigAutoField,
)


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
        null=True,
        blank=True,
        help_text='The date of the last download.'
    )
    allowed_downloads = models.PositiveIntegerField(
        null=False,
        blank=False,
        default=10,
        help_text=('The number of facility data downloads a user '
                   'can make per month.')
    )
    allowed_records_number=models.PositiveIntegerField(
        null=False,
        blank=False,
        default=1000,
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

from typing import Optional
from django.db import models
from django.utils import timezone
from django.db import transaction
from django.db.models import BigAutoField
from api.constants import FacilitiesDownloadSettings
from datetime import datetime
from django.utils.timezone import make_aware

from api.models.facility_download_limit_manager import (
    FacilityDownloadLimitManager
)


def release_initial_date():
    return make_aware(datetime(2025, 6, 28))


class FacilityDownloadLimit(models.Model):
    """
    Stores the number of facility records allowed for free download per
    calendar year, the number of paid facility records for non-API
    users, the date of last update of free facilities records, and the
    date when paid facility records were purchased.
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
        default=timezone.now,
        help_text='The date when the free limit was set or updated.'
    )
    purchase_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text='The date when paid facility records were purchased.'
    )

    objects = FacilityDownloadLimitManager()

    def register_download(self, records_to_subtract):
        with transaction.atomic():
            self.refresh_from_db()
            if self.free_download_records >= records_to_subtract:
                self.free_download_records = self.free_download_records - records_to_subtract  # noqa: E501
            else:
                remaining_records = records_to_subtract - self.free_download_records  # noqa: E501
                self.free_download_records = 0
                self.paid_download_records -= remaining_records
            self.save()

    @staticmethod
    def get_or_create_user_download_limit(
        user,
        custom_date
    ) -> Optional["FacilityDownloadLimit"]:
        is_api_user = not user.is_anonymous and user.has_groups

        if is_api_user or user.is_anonymous:
            # if user is an API user we don't want to impose limits
            return None

        defaults = {'updated_at': custom_date} if custom_date else {}

        facility_download_limit, _ = FacilityDownloadLimit \
            .objects.get_or_create(user=user, defaults=defaults)

        return facility_download_limit

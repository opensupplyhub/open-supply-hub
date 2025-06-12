from dateutil.relativedelta import relativedelta
from django.utils import timezone
from django.db import models

from api.constants import FacilitiesDownloadSettings


class FacilityDownloadLimitManager(models.Manager):
    def update_expired_limits(self):
        now = timezone.now()
        one_year_ago_with_leap = now - relativedelta(years=1)

        # Update free limits in bulk
        expired_free_limits = self.filter(
            updated_at__lt=one_year_ago_with_leap
        )
        expired_free_limits.update(
            free_download_records=FacilitiesDownloadSettings.FACILITIES_DOWNLOAD_LIMIT,
            updated_at=now
        )

        # Update paid limits in bulk
        expired_paid_limits = self.filter(
            purchase_date__lt=one_year_ago_with_leap
        ).exclude(paid_download_records=0)
        expired_paid_limits.update(paid_download_records=0)

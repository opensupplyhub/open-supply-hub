from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.utils import timezone

from api.limitation.date.date_limitation import (
    DateLimitation
)


class MonthlyDateLimitation(DateLimitation):

    def execute(self, period_start_date: datetime):
        default_tz = timezone.get_default_timezone()
        start_date = period_start_date
        if timezone.is_naive(start_date):
            start_date = timezone.make_aware(start_date, default_tz)
        start_date_utc = start_date.astimezone(timezone.utc)

        one_month_ago_utc = (
            datetime.now(tz=timezone.utc) - relativedelta(months=1)
        )
        while start_date_utc < one_month_ago_utc:
            start_date_utc = start_date_utc + relativedelta(months=1)

        self.start_date = start_date_utc

        return self

    def get_start_date(self):
        return self.start_date

    def get_api_block_until(self):
        return self.start_date + relativedelta(months=1)

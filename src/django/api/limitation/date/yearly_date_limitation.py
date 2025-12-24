from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.utils import timezone

from api.limitation.date.date_limitation import (
    DateLimitation
)


class YearlyDateLimitation(DateLimitation):

    def execute(self, period_start_date: datetime):
        utc = timezone.get_default_timezone()
        self.start_date = period_start_date

        one_year_in_past = datetime.now(tz=utc) - relativedelta(years=1)
        while (self.start_date < one_year_in_past):
            self.start_date = self.start_date + relativedelta(years=1)

        return self

    def get_start_date(self):
        return self.start_date

    def get_api_block_until(self):
        return self.start_date + relativedelta(years=1)

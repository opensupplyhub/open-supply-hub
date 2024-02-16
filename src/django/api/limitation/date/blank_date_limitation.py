from datetime import datetime
from dateutil.relativedelta import relativedelta

from api.limitation.date.date_limitation import (
    DateLimitation
)


class BlankDateLimitation(DateLimitation):

    def execute(self, period_start_date: datetime):
        self.start_date = period_start_date

        return self

    def get_start_date(self):
        return self.start_date

    def get_api_block_until(self):
        return self.start_date + relativedelta(years=1)

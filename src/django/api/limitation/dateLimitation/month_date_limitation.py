from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.utils import timezone

from api.limitation.dateLimitation.date_limitation import DateLimitation

class MonthlyDateLimitation(DateLimitation):

    def __init__(self, period_start_date: datetime):
        self.start_date = period_start_date
        self.modify_start_date()

    def modify_start_date(self):
        one_month_in_past = datetime.now(tz=timezone.utc) - relativedelta(months=1)
        while (self.start_date < one_month_in_past):
            self.start_date = self.start_date + relativedelta(months=1)
    
    def get_start_date(self):
        return self.start_date
    
    def get_api_block_until(self):
        return  self.start_date + relativedelta(months=1)
from datetime import datetime
from dateutil.relativedelta import relativedelta

from api.limitation.dateLimitation.date_limitation import DateLimitation

class YearlyDateLimitation(DateLimitation):

    def __init__(self, period_start_date: datetime):
        self.prepare_start_date(period_start_date)
        self.__modify()
    
    def __modify(self):
        one_year_in_past = datetime.now(tz=self.utc) - relativedelta(years=1)
        while (self.start_date < one_year_in_past):
            self.start_date = self.start_date + relativedelta(years=1)

    def get_start_date(self):
        return self.start_date
    
    def get_api_block_until(self):
        return  self.start_date + relativedelta(years=1)
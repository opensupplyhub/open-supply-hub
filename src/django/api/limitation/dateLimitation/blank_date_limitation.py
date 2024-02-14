from datetime import datetime

from api.limitation.dateLimitation.yearly_date_limitation import YearlyDateLimitation

class BlankDateLimitation(YearlyDateLimitation):

    def __init__(self, period_start_date: datetime):
        self.prepare_start_date(period_start_date)
        self.__modify()
    
    def __modify(self):
        pass
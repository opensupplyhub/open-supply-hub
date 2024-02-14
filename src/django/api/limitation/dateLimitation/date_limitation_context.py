from api.limitation.dateLimitation.date_limitation import DateLimitation
from api.limitation.dateLimitation.blank_date_limitation import BlankDateLimitation
from api.limitation.dateLimitation.month_date_limitation import MonthlyDateLimitation
from api.limitation.dateLimitation.yearly_date_limitation import YearlyDateLimitation

class DateLimitationContext:
    __dateLimitation: DateLimitation

    def __init__(self, renewal_period, start_date):
        self.__dateLimitation = BlankDateLimitation(start_date)

        if renewal_period == 'MONTHLY':
            self.__dateLimitation = MonthlyDateLimitation(start_date)
        if renewal_period == 'YEARLY':
            self.__dateLimitation = YearlyDateLimitation(start_date)
        

    def execute(self) -> DateLimitation:
        return self.__dateLimitation
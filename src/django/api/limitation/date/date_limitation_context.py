from datetime import datetime

from api.limitation.date.date_limitation import (
    DateLimitation
)
from api.limitation.date.blank_date_limitation import (
    BlankDateLimitation
)
from api.limitation.date.monthly_date_limitation import (
    MonthlyDateLimitation
)
from api.limitation.date.yearly_date_limitation import (
    YearlyDateLimitation
)


class DateLimitationContext:
    __dateLimitation: DateLimitation

    def __init__(self, renewal_period, start_date):
        date = self.__prepare_start_date(start_date)
        self.__dateLimitation = BlankDateLimitation(date)

        if renewal_period == 'MONTHLY':
            self.__dateLimitation = MonthlyDateLimitation(date)
        if renewal_period == 'YEARLY':
            self.__dateLimitation = YearlyDateLimitation(date)

    def execute(self) -> DateLimitation:
        return self.__dateLimitation

    def __prepare_start_date(self, date: datetime):
        MINIMUM_DAY_TO_ROUND = 28
        END_OF_THE_YEAR = 12

        if date.day > MINIMUM_DAY_TO_ROUND:
            if date.month == END_OF_THE_YEAR:
                return date.replace(day=1,
                                    month=1,
                                    year=date.year + 1)

            return date.replace(day=1,
                                month=date.month + 1)

        return date

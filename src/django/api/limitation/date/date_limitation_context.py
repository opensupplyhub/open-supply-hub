from datetime import datetime

from api.limitation.date.date_limitation import (
    DateLimitation
)


class DateLimitationContext:
    __date_limitation: DateLimitation

    def setStrategy(self, strategy: DateLimitation):
        self.__date_limitation = strategy

    def execute(self, start_date) -> DateLimitation:
        date = self.__prepare_start_date(start_date)
        return self.__date_limitation.execute(date)

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

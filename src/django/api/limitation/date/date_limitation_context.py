from api.limitation.date.date_limitation import (
    DateLimitation
)

from api.limitation.date.date_limitation_utils import (
    DateLimitationUtils
)


class DateLimitationContext:
    __date_limitation: DateLimitation

    utils = DateLimitationUtils()

    def set_strategy(self, strategy: DateLimitation):
        self.__date_limitation = strategy

    def execute(self, start_date) -> DateLimitation:
        date = self.utils.prepare_start_date(start_date)
        return self.__date_limitation.execute(date)

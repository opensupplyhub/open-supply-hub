from datetime import datetime


class DateLimitationUtils:

    def prepare_start_date(self, date: datetime):
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

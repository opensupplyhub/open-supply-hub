from abc import ABC, abstractmethod
from datetime import datetime
from django.utils import timezone

class DateLimitation(ABC):
    utc = timezone.utc

    start_date: datetime

    @abstractmethod
    def __init__(self, period_start_date: datetime):
        pass

    @abstractmethod
    def get_start_date(self):
        pass

    @abstractmethod
    def get_api_block_until(self):
        pass

    def __modify(self):
        pass
    
    def prepare_start_date(self, date: datetime):
        MINIMUM_DAY_TO_ROUND = 28
        END_OF_THE_YEAR = 12

        if date.day > MINIMUM_DAY_TO_ROUND:
            if date.month == END_OF_THE_YEAR:
                self.start_date = date.replace(day=1,
                                               month=1,
                                               year=date.year + 1)

            self.start_date = date.replace(day=1,
                                           month=date.month + 1)
        
        self.start_date = date
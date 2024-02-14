from abc import ABC, abstractmethod
from datetime import datetime


class DateLimitation(ABC):
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
    
    @abstractmethod
    def modify_start_date(self):
        pass

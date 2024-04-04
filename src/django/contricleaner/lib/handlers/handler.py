from abc import ABC, abstractmethod
from typing import List
from contricleaner.lib.dto.list_dto import ListDTO


class Handler(ABC):

    @abstractmethod
    def setNext(self, next):
        pass

    @abstractmethod
    def handle(self, rows: List[dict]) -> ListDTO:
        pass

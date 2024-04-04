from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List

from contricleaner.lib.dto.list_dto import ListDTO


class ListRowHandler(ABC):
    _next: ListRowHandler

    def set_next(self, next: ListRowHandler):
        self._next = next

    @abstractmethod
    def handle(self, rows: List[dict]) -> ListDTO:
        pass

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Dict

from contricleaner.lib.dto.list_dto import ListDTO
from contricleaner.lib.exceptions.handler_not_set_error \
    import HandlerNotSetError


class ListRowHandler(ABC):
    _next: ListRowHandler

    def set_next(self, next: ListRowHandler):
        self._next = next

    @abstractmethod
    def handle(self, rows: List[Dict]) -> ListDTO:
        if self._next:
            return self._next.handle(rows)

        raise HandlerNotSetError("Next Handler isn't set.")

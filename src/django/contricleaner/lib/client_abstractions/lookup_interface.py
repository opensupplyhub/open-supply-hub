from abc import ABC, abstractmethod
from typing import Any


class LookupInterface(ABC):
    def __init__(self, lookup_field: str):
        self.lookup_field = lookup_field

    @abstractmethod
    def get(self, key: Any) -> dict:
        pass

    @abstractmethod
    def bulk_get(self, keys: list) -> dict:
        pass

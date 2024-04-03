from abc import ABC, abstractmethod
from typing import List


class EarlyValidator(ABC):

    @abstractmethod
    def validate(self, rows: List[dict]) -> dict:
        pass
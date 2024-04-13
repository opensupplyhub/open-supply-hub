from abc import ABC, abstractmethod
from typing import List


class PreValidator(ABC):

    @abstractmethod
    def validate(self, rows: List[dict]) -> dict:
        pass

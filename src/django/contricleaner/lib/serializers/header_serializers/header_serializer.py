from abc import ABC, abstractmethod
from typing import List


class HeaderSerializer(ABC):

    @abstractmethod
    def validate(self, headers: List[str], current: dict) -> dict:
        pass

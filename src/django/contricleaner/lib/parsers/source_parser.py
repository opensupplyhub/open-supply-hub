from typing import List
from abc import ABC, abstractmethod


class SourceParser(ABC):
    @abstractmethod
    def get_parsed_rows(self) -> List[dict]:
        pass

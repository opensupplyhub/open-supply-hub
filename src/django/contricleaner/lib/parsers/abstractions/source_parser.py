from typing import List, Dict
from abc import ABC, abstractmethod


class SourceParser(ABC):
    @abstractmethod
    def get_parsed_rows(self) -> List[Dict]:
        pass

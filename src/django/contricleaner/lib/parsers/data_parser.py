from typing import List
from abc import ABC, abstractmethod


class DataParser(ABC):
    @abstractmethod
    def parse(self, entity, request):
        pass

    @abstractmethod
    def get_parsed_rows(self) -> List[dict]:
        pass

from typing import List
from abc import ABC, abstractmethod


class SourceParser(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def parsed_header(self) -> List[str]:
        pass

    @abstractmethod
    def parsed_rows(self) -> List[dict]:
        pass

from typing import List
from abc import ABC, abstractmethod

from django.core.files.base import File


class FileParser(ABC):
    '''
    Abstract FileParser class for parsers related to file parsing.
    '''

    def __init__(self, file: File) -> None:
        self._file = file

    @staticmethod
    @abstractmethod
    def _parse(file: File) -> List[dict]:
        pass

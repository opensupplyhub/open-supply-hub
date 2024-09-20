from typing import List
from abc import ABC, abstractmethod

from django.db.models.fields.files import FieldFile


class FileParser(ABC):
    '''
    Abstract FileParser class for parsers related to file parsing.
    '''

    def __init__(self, file: FieldFile) -> None:
        self._file = file

    @staticmethod
    @abstractmethod
    def _parse(file: FieldFile) -> List[dict]:
        pass

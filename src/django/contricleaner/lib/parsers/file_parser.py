from typing import List, Union
from abc import ABC, abstractmethod

from django.core.files.uploadedfile import (
    InMemoryUploadedFile,
    TemporaryUploadedFile
)


class FileParser(ABC):
    '''
    Abstract FileParser class for parsers related to file parsing.
    '''

    def __init__(self,
                 file: Union[InMemoryUploadedFile, TemporaryUploadedFile]
                 ) -> None:
        self._file = file

    @staticmethod
    @abstractmethod
    def _parse(
            file: Union[InMemoryUploadedFile, TemporaryUploadedFile]
            ) -> List[dict]:
        pass

    @staticmethod
    def remove_empty_values_from_row_dict(row_dict: dict) -> dict:
        '''
        Remove key-value pairs with empty string values from a row dictionary
        to prevent errors when cells are left empty, which is acceptable for
        list uploads where not all cells need to be filled with data under
        one column.
        '''
        return {key: value for key, value in row_dict.items() if value != ''}

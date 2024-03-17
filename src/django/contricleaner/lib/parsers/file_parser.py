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

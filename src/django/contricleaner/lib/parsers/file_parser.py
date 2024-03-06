import re
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
    def _clean_row(row: str) -> str:
        invalid_keywords = ['N/A', 'n/a']
        replaced_value = FileParser.__replace_invalid_data(
            row, invalid_keywords
        )
        return FileParser.__cleanup_data(replaced_value)

    @staticmethod
    def __replace_invalid_data(value: str, invalid_keywords: List[str]) -> str:
        result_value = value
        for keyword in invalid_keywords:
            # Remove invalid keywords if exist
            result_value = result_value.replace(keyword, '')
        return result_value

    @staticmethod
    def __cleanup_data(value: str) -> str:
        dup_pattern = ',' + '{2,}'
        # Remove duplicates commas if exist
        result_value = re.sub(dup_pattern, ',', value)
        # Remove comma in the end of the string if exist
        result_value = result_value.rstrip(',')
        # Remove extra spaces if exist
        return result_value.strip()

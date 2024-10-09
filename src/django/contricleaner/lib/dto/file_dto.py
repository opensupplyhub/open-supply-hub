from typing import NamedTuple
from io import BytesIO


class FileDTO(NamedTuple):
    file: BytesIO
    file_name: str

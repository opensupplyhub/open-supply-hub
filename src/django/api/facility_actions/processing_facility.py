from abc import ABC, abstractmethod
from typing import Union

from api.models.facility.facility_list_item import FacilityListItem
from api.models.source import Source
from contricleaner.lib.dto.row_dto import RowDTO

from rest_framework.response import Response


class ProcessingFacility(ABC):
    '''
    Abstract class for facility processing received from both
    API requests and list uploads.
    '''

    @abstractmethod
    def process_facility(self) -> Union[Response, None]:
        pass

    @staticmethod
    @abstractmethod
    def _create_facility_list_item(
        source: Source, row: RowDTO, idx: int, header_str: str
    ) -> FacilityListItem:
        pass

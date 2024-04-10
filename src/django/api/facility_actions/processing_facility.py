import logging
from abc import ABC, abstractmethod

from api.models.facility.facility_list_item import FacilityListItem
from api.models.source import Source
from contricleaner.lib.dto.row_dto import RowDTO

# initialize logger
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO
)
log = logging.getLogger(__name__)


class ProcessingFacility(ABC):
    '''
    Abstract class for facility processing both via API and list uploads.
    '''

    @abstractmethod
    def process_facility(self):
        pass

    @staticmethod
    def _create_facility_list_item(
        source: Source, row: RowDTO, idx: int, header_str: str
    ) -> FacilityListItem:
        return FacilityListItem.objects.create(
            source=source,
            row_index=idx,
            raw_data=','.join(row.raw_json.values()),
            raw_json=row.raw_json,
            raw_header=header_str,
            name=row.name,
            clean_name=row.clean_name,
            address=row.address,
            clean_address=row.clean_address,
            country_code=row.country_code,
            sector=row.sector,
        )

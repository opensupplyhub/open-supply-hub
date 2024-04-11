import logging
from abc import ABC, abstractmethod
from typing import List

from api.models.contributor.contributor import Contributor
from api.models.facility.facility_list_item import FacilityListItem
from api.models.nonstandart_field import NonstandardField
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

    @staticmethod
    def _create_nonstandard_fields(fields: List[str], contributor: Contributor) -> None:
        unique_fields = list(set(fields))

        existing_fields = (
            NonstandardField
            .objects
            .filter(contributor=contributor)
            .values_list('column_name', flat=True)
        )
        new_fields = filter(
            lambda f: f not in existing_fields, unique_fields
        )
        standard_fields = [
            'sector', 'country', 'name', 'address', 'lat', 'lng',
        ]
        nonstandard_fields = filter(
            lambda f: f.lower() not in standard_fields, new_fields
        )

        for field in nonstandard_fields:
            (
                NonstandardField
                .objects
                .create(
                    contributor=contributor,
                    column_name=field
                )
            )

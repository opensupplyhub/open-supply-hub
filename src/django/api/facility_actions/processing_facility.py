from abc import ABC, abstractmethod
from typing import KeysView, Union

from api.models.contributor.contributor import Contributor
from api.models.facility.facility_list_item import FacilityListItem
from api.models.nonstandard_field import NonstandardField
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

    @staticmethod
    def _create_nonstandard_fields(
        fields: KeysView[str], contributor: Contributor
    ) -> None:
        unique_fields = list(set(fields))

        existing_fields = NonstandardField.objects.filter(
            contributor=contributor
        ).values_list('column_name', flat=True)
        new_fields = filter(lambda f: f not in existing_fields, unique_fields)
        standard_fields = [
            'sector',
            'country',
            'name',
            'address',
            'lat',
            'lng',
        ]
        nonstandard_fields = filter(
            lambda f: f.lower() not in standard_fields, new_fields
        )

        for field in nonstandard_fields:
            (
                NonstandardField.objects.create(
                    contributor=contributor, column_name=field
                )
            )

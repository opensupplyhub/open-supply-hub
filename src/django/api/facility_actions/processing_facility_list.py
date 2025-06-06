import logging
import traceback
from typing import Any, Dict, Optional, Set, List, Union

from django.contrib.gis.geos import Point
from django.utils import timezone

from api.constants import FileHeaderField, ProcessingAction
from api.extended_fields import create_extendedfields_for_single_item
from api.facility_actions.processing_facility import ProcessingFacility
from api.models.facility.facility_list import FacilityList
from api.models.facility.facility_list_item import FacilityListItem
from api.models.source import Source
from api.views.fields.create_nonstandard_fields import (
    create_nonstandard_fields
)
from contricleaner.lib.dto.list_dto import ListDTO
from contricleaner.lib.dto.row_dto import RowDTO
from oar.rollbar import report_error_to_rollbar

log = logging.getLogger(__name__)


class ProcessingFacilityList(ProcessingFacility):
    '''
    Class to process a facility list.
    '''

    def __init__(self, processing_input: Dict[str, Any]) -> None:
        self.__facility_list: FacilityList = processing_input['facility_list']
        # It can be None if there are CC internal errors.
        self.__contri_cleaner_processed_data: Union[ListDTO, None] = \
            processing_input.get('contri_cleaner_processed_data')
        self.__parsing_started: str = processing_input['parsing_started']
        # It can be None if there aren't CC internal errors.
        self.__internal_errors: Union[List[Dict], None] = \
            processing_input.get('internal_errors')

    def process_facility(self) -> None:
        if self.__internal_errors:
            self.__handle_cc_internal_errors()
            return
        if self.__contri_cleaner_processed_data.errors:
            self.__handle_list_level_errors()
            return

        rows = self.__contri_cleaner_processed_data.rows
        header_row_keys = rows[0].raw_json.keys()
        header_str = ','.join(header_row_keys)

        self.__facility_list.header = header_str
        self.__facility_list.save()

        create_nonstandard_fields(
            header_row_keys,
            self.__facility_list.source.contributor
        )

        is_geocoded: bool = False
        parsed_items: Set[str] = set()

        for idx, row in enumerate(rows):
            # Created a partially filled FacilityListItem to save valid data
            # and to provide an item for saving any errors that may exist
            # below.
            item = self._create_facility_list_item(
                self.__facility_list.source, row, idx, header_str
            )
            log.info(f'[List Upload] FacilityListItem created. Id {item.id}!')

            self.__handle_row_errors(item, row)

            if item.status != FacilityListItem.ERROR_PARSING:
                item.sector = row.sector
                item.country_code = row.country_code
                item.name = row.name
                item.clean_name = row.clean_name
                item.address = row.address
                item.clean_address = row.clean_address
                try:
                    self.__process_valid_item(item, row)
                except Exception as e:
                    self.__handle_processing_exception(item, e)

            self.__finalize_item_processing(item, is_geocoded, parsed_items)

    @staticmethod
    def _create_facility_list_item(
        source: Source, row: RowDTO, idx: int, header_str: str
    ) -> FacilityListItem:
        return FacilityListItem.objects.create(
            row_index=idx,
            raw_data=','.join(f'"{value}"' for value in row.raw_json.values()),
            raw_json=row.raw_json,
            raw_header=header_str,
            sector=[],
            source=source,
            source_uuid=source
        )

    def __handle_cc_internal_errors(self) -> None:
        self.__facility_list.parsing_errors = self.__internal_errors
        self.__facility_list.save()
        log.error(
            '[List Upload] CC Internal Errors: '
            f'{self.__internal_errors}'
        )

    def __handle_list_level_errors(self) -> None:
        self.__facility_list.parsing_errors = \
            self.__contri_cleaner_processed_data.errors
        self.__facility_list.save()
        log.error(
            '[List Upload] CC List-Level Errors: '
            f'{self.__contri_cleaner_processed_data.errors}'
        )

    def __handle_row_errors(self, item: FacilityListItem, row: RowDTO) -> None:
        if row.errors:
            stringified_cc_err_messages = '\n'.join(
                [f"{error['message']}" for error in row.errors]
            )
            log.error(
                f'[List Upload] CC Parsing Error: '
                f'{stringified_cc_err_messages}'
            )
            log.info(f'[List Upload] FacilityListItem Id: {item.id}')
            item.status = FacilityListItem.ERROR_PARSING
            item.processing_results.append(
                {
                    'action': ProcessingAction.PARSE,
                    'started_at': self.__parsing_started,
                    'error': True,
                    'message': str(stringified_cc_err_messages),
                    'trace': traceback.format_exc(),
                    'finished_at': str(timezone.now()),
                }
            )

    def __process_valid_item(
        self, item: FacilityListItem, row: RowDTO
    ) -> None:
        lat: Optional[float] = row.fields.get(FileHeaderField.LAT)
        lng: Optional[float] = row.fields.get(FileHeaderField.LNG)

        if lat and lng:
            item.geocoded_point = Point(lng, lat)
            self.is_geocoded = True

        create_extendedfields_for_single_item(item, row.fields)

    def __handle_processing_exception(
        self, item: FacilityListItem, exception: Exception
    ) -> None:
        error_message = (
            f'[List Upload] Creation of ExtendedField error: {exception}'
        )
        log.error(error_message)
        report_error_to_rollbar(
            message=error_message,
            extra_data={'affected_list': str(self.__facility_list)}
        )
        log.info(f'[List Upload] FacilityListItem Id: {item.id}')

        item.status = FacilityListItem.ERROR_PARSING
        item.processing_results.append(
            {
                'action': ProcessingAction.PARSE,
                'started_at': self.__parsing_started,
                'error': True,
                'message': str(exception),
                'trace': traceback.format_exc(),
                'finished_at': str(timezone.now()),
            }
        )

    def __finalize_item_processing(
        self, item: FacilityListItem, is_geocoded: bool, parsed_items: Set[str]
    ) -> None:
        if item.status != FacilityListItem.ERROR_PARSING:
            item.status = FacilityListItem.PARSED
            item.processing_results.append(
                {
                    'action': ProcessingAction.PARSE,
                    'started_at': self.__parsing_started,
                    'error': False,
                    'finished_at': str(timezone.now()),
                    'is_geocoded': is_geocoded,
                }
            )

            core_fields = '{}-{}-{}'.format(
                item.country_code, item.clean_name, item.clean_address
            )
            if core_fields in parsed_items:
                item.status = FacilityListItem.DUPLICATE
            else:
                parsed_items.add(core_fields)
        item.save()

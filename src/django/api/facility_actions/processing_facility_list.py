import logging
import traceback
from typing import Any, Dict

from api.constants import FileHeaderField, ProcessingAction
from api.extended_fields import create_extendedfields_for_single_item
from api.facility_actions.processing_facility import ProcessingFacility
from api.models.facility.facility_list import FacilityList
from api.models.facility.facility_list_item import FacilityListItem
from api.models.source import Source
from oar.rollbar import report_error_to_rollbar
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from django.contrib.gis.geos import Point
from django.utils import timezone

# initialize logger
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO
)
log = logging.getLogger(__name__)


class ProcessingFacilityList(ProcessingFacility):
    '''
    Class to process a facility list.
    '''

    def __init__(self, processing_input: Dict[str, Any]) -> None:
        self.__uploaded_file = processing_input['uploaded_file']
        self.__processed_data = processing_input['processed_data']
        self.__contributor = processing_input['contributor']
        self.__parsing_started = processing_input['parsing_started']
        self.__serializer_method = processing_input['serializer_method']
        self.__name = processing_input['name']
        self.__description = processing_input['description']
        self.__replaces = processing_input['replaces']

    def _process_facility(self) -> Response:
        # handle processing errors
        if self.__processed_data.errors:
            log.error(
                '[List Upload] CC Validation Errors: '
                f'{self.__processed_data.errors}'
            )
            error_messages = [
                str(error['message']) for error in self.__processed_data.errors
            ]
            raise ValidationError(error_messages)

        rows = self.__processed_data.rows
        header_row_keys = rows[0].raw_json.keys()
        header_str = ','.join(header_row_keys)

        new_list = self.__create_list(header_str)
        log.info(f'[List Upload] FacilityList created. Id {new_list.id}!')

        self._create_nonstandard_fields(header_row_keys, self.__contributor)

        source = self._create_source(new_list)
        log.info(f'[List Upload] Source created. Id {source.id}!')

        is_geocoded = False
        parsed_items = set()

        for idx, row in enumerate(rows):
            # Created a partially filled FacilityListItem to save valid data
            # and to provide an item for saving any errors that may exist
            # below.
            item = self._create_facility_list_item(
                source, row, idx, header_str
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

        serializer = self.__serializer_method(new_list)
        return Response(serializer.data)

    def __create_list(self, header_str):
        return FacilityList.objects.create(
            name=self.__name,
            description=self.__description,
            file_name=self.__uploaded_file.name,
            file=self.__uploaded_file,
            header=header_str,
            replaces=self.__replaces,
            match_responsibility=self.__contributor.match_responsibility,
        )

    def _create_source(self, new_list):
        return Source.objects.create(
            contributor=self.__contributor,
            source_type=Source.LIST,
            facility_list=new_list,
        )

    @staticmethod
    def _create_facility_list_item(source, row, idx, header_str):
        return FacilityListItem.objects.create(
            row_index=idx,
            raw_data=','.join(f'"{value}"' for value in row.raw_json.values()),
            raw_json=row.raw_json,
            raw_header=header_str,
            sector=[],
            source=source,
        )

    def __handle_row_errors(self, item, row):
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

    def __process_valid_item(self, item, row):
        if (
            FileHeaderField.LAT in row.fields.keys()
            and FileHeaderField.LNG in row.fields.keys()
        ):
            # TODO: Move floating to the ContriCleaner library.
            lat = float(row.fields[FileHeaderField.LAT])
            lng = float(row.fields[FileHeaderField.LNG])
            item.geocoded_point = Point(lng, lat)
            self.is_geocoded = True

        create_extendedfields_for_single_item(item, row.fields)

    def __handle_processing_exception(self, item, exception):
        request = self.__processing_input['request']

        log.error(
            f'[List Upload] Creation of ExtendedField error: {exception}'
        )
        report_error_to_rollbar(
            request=request, file=self.__uploaded_file, exception=exception
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

    def __finalize_item_processing(self, item, is_geocoded, parsed_items):
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

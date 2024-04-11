import logging
import traceback

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
    def __init__(
        self,
        processing_data,
    ) -> None:
        self.__processing_data = processing_data

    def process_facility(self):
        request = self.__processing_data.get('request')
        name = self.__processing_data.get('name')
        description = self.__processing_data.get('description')
        uploaded_file = self.__processing_data.get('uploaded_file')
        replaces = self.__processing_data.get('replaces')
        processed_data = self.__processing_data.get('processed_data')
        contributor = self.__processing_data.get('contributor')
        parsing_started = self.__processing_data.get('parsing_started')
        serializer_method = self.__processing_data.get('serializer_method')

        # handle processing errors
        if processed_data.errors:
            log.error(
                f'[List Upload] CC Validation Errors: {processed_data.errors}'
            )
            error_messages = [
                str(error['message']) for error in processed_data.errors
            ]
            raise ValidationError(error_messages)

        rows = processed_data.rows
        header_row_keys = rows[0].raw_json.keys()
        header_str = ','.join(header_row_keys)
        new_list = FacilityList(
            name=name,
            description=description,
            file_name=uploaded_file.name,
            file=uploaded_file,
            header=header_str,
            replaces=replaces,
            match_responsibility=contributor.match_responsibility,
        )
        new_list.save()
        log.info(f'[List Upload] FacilityList created. Id {new_list.id}!')

        self._create_nonstandard_fields(header_row_keys, contributor)

        source = Source.objects.create(
            contributor=contributor,
            source_type=Source.LIST,
            facility_list=new_list,
        )
        log.info(f'[List Upload] Source created. Id {source.id}!')

        is_geocoded = False
        parsed_items = set()
        for idx, row in enumerate(rows):
            item = self._create_facility_list_item(
                source, row, idx, header_str
            )
            log.info(f'[List Upload] FacilityListItem created. Id {item.id}!')

            row_errors = row.errors
            if len(row_errors) > 0:
                stringified_cc_err_messages = '\n'.join(
                    [f"{error['message']}" for error in row_errors]
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
                        'started_at': parsing_started,
                        'error': True,
                        'message': stringified_cc_err_messages,
                        'trace': traceback.format_exc(),
                        'finished_at': str(timezone.now()),
                    }
                )

            if item.status != FacilityListItem.ERROR_PARSING:
                try:
                    if (
                        FileHeaderField.LAT in row.fields.keys()
                        and FileHeaderField.LNG in row.fields.keys()
                    ):
                        # TODO: Move floating to the ContriCleaner library.
                        lat = float(row.fields[FileHeaderField.LAT])
                        lng = float(row.fields[FileHeaderField.LNG])
                        item.geocoded_point = Point(lng, lat)
                        is_geocoded = True

                    create_extendedfields_for_single_item(item, row.fields)
                except Exception as e:
                    log.error(
                        f'[List Upload] Creation of ExtendedField error: {e}'
                    )
                    report_error_to_rollbar(
                        request=request, file=uploaded_file, exception=e
                    )
                    log.info(f'[List Upload] FacilityListItem Id: {item.id}')
                    item.status = FacilityListItem.ERROR_PARSING
                    item.processing_results.append(
                        {
                            'action': ProcessingAction.PARSE,
                            'started_at': parsing_started,
                            'error': True,
                            'message': str(e),
                            'trace': traceback.format_exc(),
                            'finished_at': str(timezone.now()),
                        }
                    )

            if item.status != FacilityListItem.ERROR_PARSING:
                item.status = FacilityListItem.PARSED
                item.processing_results.append(
                    {
                        'action': ProcessingAction.PARSE,
                        'started_at': parsing_started,
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

            serializer = serializer_method(new_list)

        return Response(serializer.data)

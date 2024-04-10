import logging
import traceback

from api.constants import FileHeaderField, ProcessingAction
from api.extended_fields import (
    create_extendedfields_for_listitem,
    create_extendedfields_for_single_item,
)
from api.facility_actions.processing_facility import ProcessingFacility
from api.models.facility.facility_list_item import FacilityListItem
from api.views.fields.create_nonstandard_fields import (
    create_nonstandard_fields,
)
from rest_framework.response import Response

from django.contrib.gis.geos import Point
from django.utils import timezone

# initialize logger
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO
)
log = logging.getLogger(__name__)


class ProcessingFacilityList(ProcessingFacility):
    def process_facility(
        request,
        rows,
        source,
        header_str,
        header_row_keys,
        contributor,
        serializer,
    ):
        parsing_started = str(timezone.now())

        create_nonstandard_fields(header_row_keys, contributor)

        log.info(f'[List Upload] Source created. Id {source.id}!')
        is_geocoded = False
        parsed_items = set()

        for idx, row in enumerate(rows):
            item = ProcessingFacility.create_facility_list_item(
                source, row, idx, header_str
            )

            log.info(f'[List Upload] FacilityListItem created. Id {item.id}!')
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

                create_extendedfields_for_listitem(
                    item, list(row.fields.keys()), list(row.fields.values())
                )
            except Exception as e:
                log.error(
                    f'[List Upload] Creation of ExtendedField error: {e}'
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
                        'is_geocoded': is_geocoded,
                    }
                )

            row_errors = row.errors
            if len(row_errors) > 0:
                stringified_message = '\n'.join(
                    [f"{error['message']}" for error in row_errors]
                )
                log.error(
                    f'[List Upload] CC Parsing Error: {stringified_message}'
                )
                log.info(f'[List Upload] FacilityListItem Id: {item.id}')
                item.status = FacilityListItem.ERROR_PARSING
                item.processing_results.append(
                    {
                        'action': ProcessingAction.PARSE,
                        'started_at': parsing_started,
                        'error': True,
                        'message': stringified_message,
                        'trace': traceback.format_exc(),
                        'finished_at': str(timezone.now()),
                        'is_geocoded': is_geocoded,
                    }
                )
            else:
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

            if item.status != FacilityListItem.ERROR_PARSING:
                core_fields = '{}-{}-{}'.format(
                    item.country_code, item.clean_name, item.clean_address
                )
                if core_fields in parsed_items:
                    item.status = FacilityListItem.DUPLICATE
                else:
                    parsed_items.add(core_fields)

            item.save()

        return Response(serializer.data)

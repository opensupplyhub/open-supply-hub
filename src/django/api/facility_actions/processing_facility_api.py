import asyncio
import logging
import traceback

from api.constants import ErrorMessages, ProcessingAction
from api.extended_fields import create_extendedfields_for_single_item
from api.facility_actions.processing_facility import ProcessingFacility
from api.geocoding import geocode_address
from api.kafka_producer import produce_message_match_process
from api.models.facility.facility_list_item import FacilityListItem
from api.models.facility.facility_list_item_temp import FacilityListItemTemp
from api.models.source import Source
from api.processing import handle_external_match_process_result
from api.views.fields.create_nonstandard_fields import (
    create_nonstandard_fields,
)
from rest_framework import status
from rest_framework.response import Response

from django.contrib.gis.geos import Point
from django.core import exceptions as core_exceptions
from django.utils import timezone

# initialize logger
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO
)
log = logging.getLogger(__name__)


class ProcessingFacilityAPI(ProcessingFacility):

    def __init__(
        self, request, processed_data, source: Source, should_create: bool
    ) -> None:
        self.__request = request
        self.__processed_data = processed_data
        self.__source = source
        self.__should_create = should_create

    def process_facility(self):
        # handle processing errors
        if self.__processed_data.errors:
            log.error(
                f'[API Upload] CC Validation Errors: {self.__processed_data.errors}'
            )
            return Response({
                "message": "The provided data could not be processed",
                "errors": self.__processed_data.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        rows = self.__processed_data.rows
        row = rows[0]

        # handle parsing errors
        if row.errors:
            log.error(f'[API Upload] CC Parsing Errors: {row.errors}')
            return Response(
                {
                    "message": "The provided data could not be parsed",
                    "errors": row.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        parse_started = str(timezone.now())

        create_nonstandard_fields(
            list(row.fields.keys()), self.__request.user.contributor
        )

        item = self._create_facility_list_item(
            self.__source, row, 0, ''
        )

        item.status = (FacilityListItem.PARSED,)
        item.processing_results = [
            {
                'action': ProcessingAction.PARSE,
                'started_at': parse_started,
                'error': False,
                'finished_at': str(timezone.now()),
                'is_geocoded': False,
            }
        ]

        log.info(f'[API Upload] Source created. Id: {self.__source.id}')
        log.info(f'[API Upload] Source is public: {self.__source.is_public}')
        log.info(f'[API Upload] Source should create: {self.__source.create}')
        log.info(f'[API Upload] FacilityListItem created. Id: {item.id}')

        result = {
            'matches': [],
            'item_id': item.id,
            'geocoded_geometry': None,
            'geocoded_address': None,
            'status': item.status,
        }

        try:
            create_extendedfields_for_single_item(item, row.fields)
        except (core_exceptions.ValidationError, ValueError) as exc:
            error_message = ''

            if isinstance(exc, ValueError):
                error_message = str(exc)
            else:
                error_message = exc.message

            item.status = FacilityListItem.ERROR_PARSING
            item.processing_results.append(
                {
                    'action': ProcessingAction.PARSE,
                    'started_at': parse_started,
                    'error': True,
                    'message': error_message,
                    'trace': traceback.format_exc(),
                    'finished_at': str(timezone.now()),
                }
            )
            item.save()
            result['status'] = item.status
            result['message'] = error_message
            log.error(
                '[API Upload] Creation of ExtendedField error: '
                f'{error_message}'
            )
            log.info(f'[API Upload] FacilityListItem Id: {item.id}')
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        geocode_started = str(timezone.now())
        log.info(
            '[API Upload] Started Geocode process. '
            f'FacilityListItem Id: {item.id}.'
        )
        log.info(
            f'[API Upload] Address: {row.address}, '
            f'Country Code: {row.country_code}'
        )
        try:
            geocode_result = geocode_address(
                row.address, row.country_code
            )
            if geocode_result['result_count'] > 0:
                item.status = FacilityListItem.GEOCODED
                item.geocoded_point = Point(
                    geocode_result["geocoded_point"]["lng"],
                    geocode_result["geocoded_point"]["lat"],
                )
                item.geocoded_address = geocode_result["geocoded_address"]

                result['geocoded_geometry'] = {
                    'type': 'Point',
                    'coordinates': [
                        geocode_result["geocoded_point"]["lng"],
                        geocode_result["geocoded_point"]["lat"],
                    ],
                }
                result['geocoded_address'] = item.geocoded_address
            else:
                item.status = FacilityListItem.GEOCODED_NO_RESULTS
                result['status'] = item.status
                result['message'] = ErrorMessages.GEOCODED_NO_RESULTS

            item.processing_results.append(
                {
                    'action': ProcessingAction.GEOCODE,
                    'started_at': geocode_started,
                    'error': False,
                    'skipped_geocoder': False,
                    'data': geocode_result['full_response'],
                    'finished_at': str(timezone.now()),
                }
            )

            item.save()
            # [A/B Test] OSHUB-507
            FacilityListItemTemp.copy(item)
        except Exception as exc:
            item.status = FacilityListItem.ERROR_GEOCODING
            item.processing_results.append(
                {
                    'action': ProcessingAction.GEOCODE,
                    'started_at': geocode_started,
                    'error': True,
                    'message': str(exc),
                    'trace': traceback.format_exc(),
                    'finished_at': str(timezone.now()),
                }
            )
            item.save()
            result['status'] = item.status
            log.error(f'[API Upload] Geocode Error: {str(exc)}')
            log.info(f'[API Upload] FacilityListItem Id: {item.id}')
            log.info(
                f'[API Upload] Address: {row.address}, '
                f'Country Code: {row.country_code}'
            )
            return Response(
                result, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        if item.status == FacilityListItem.GEOCODED:
            log.info('[API Upload] Trying to start Match process!')
            log.info(f'[API Upload] FacilityListItem Id: {item.id}')
            log.info(f'[API Upload] Source Id: {item.id}')
            # Handle and produce message to Kafka with source_id data
            timer = 0
            timeout = 25
            fli_temp = None
            while True:
                if timer > timeout:
                    break
                fli_temp = FacilityListItemTemp.objects.get(
                    source=self.__source.id
                )
                if fli_temp.status == FacilityListItemTemp.GEOCODED:
                    log.info('[API Upload] Started Match process!')
                    log.info(f'[API Upload] FacilityListItem Id: {item.id}')
                    log.info(
                        f'[API Upload] FacilityListItemTemp Id: {fli_temp.id}'
                    )
                    log.info(f'[API Upload] Source Id: {item.id}')
                    asyncio.run(
                        produce_message_match_process(self.__source.id)
                    )
                    break
                asyncio.sleep(1)
                timer = timer + 1

            # Handle results of "match" process from Dedupe Hub
            result = handle_external_match_process_result(
                fli_temp.id, result, self.__request, self.__should_create
            )

        errors_status = [
            FacilityListItem.ERROR_MATCHING,
            FacilityListItem.GEOCODED_NO_RESULTS,
        ]

        log.info(f'[API Upload] Result data: {result}')
        log.info(f'[API Upload] FacilityListItem Id: {item.id}')
        log.info(f'[API Upload] Source Id: {item.id}')

        if self.__should_create and result['status'] not in errors_status:
            return Response(result, status=status.HTTP_201_CREATED)
        else:
            return Response(result, status=status.HTTP_200_OK)

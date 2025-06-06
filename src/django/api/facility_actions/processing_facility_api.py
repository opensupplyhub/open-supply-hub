import asyncio
import logging
import traceback
from typing import Any, Dict, List, Union

from api.constants import APIErrorMessages, ProcessingAction
from api.extended_fields import create_extendedfields_for_single_item
from api.facility_actions.processing_facility import ProcessingFacility
from api.geocoding import geocode_address
from api.kafka_producer import produce_message_match_process
from api.models.contributor.contributor import Contributor
from api.models.facility.facility_list_item import FacilityListItem
from api.models.facility.facility_list_item_temp import FacilityListItemTemp
from api.models.source import Source
from api.processing import handle_external_match_process_result
from api.views.fields.create_nonstandard_fields import (
    create_nonstandard_fields,
)
from contricleaner.lib.dto.list_dto import ListDTO
from contricleaner.lib.dto.row_dto import RowDTO
from rest_framework import status
from rest_framework.response import Response
from rest_framework.request import Request

from django.contrib.gis.geos import Point
from django.core import exceptions as core_exceptions
from django.utils import timezone
from django.core.exceptions import ValidationError

log = logging.getLogger(__name__)


class ProcessingFacilityAPI(ProcessingFacility):
    '''
    Class to process a facility from an API request.
    '''

    def __init__(self, processing_input: Dict[str, Any]) -> None:
        self.__request: Request = processing_input['request']
        self.__contri_cleaner_processed_data: ListDTO = processing_input[
            'contri_cleaner_processed_data'
        ]
        self.__public_submission: bool = processing_input['public_submission']
        self.__should_create: bool = processing_input['should_create']
        self.__parsing_started: str = processing_input['parsing_started']
        self.__contributor: Contributor = self.__request.user.contributor

    def process_facility(self) -> Response:
        # handle processing errors
        if self.__contri_cleaner_processed_data.errors:
            return self.__handle_validation_errors()

        rows = self.__contri_cleaner_processed_data.rows
        header_row_keys = rows[0].raw_json.keys()
        header_str = ','.join(header_row_keys)
        row = rows[0]

        # handle parsing errors
        if row.errors:
            return self.__handle_parsing_errors(row.errors)

        source = self._create_source()

        create_nonstandard_fields(header_row_keys, self.__contributor)

        row_index = 0
        item = self._create_facility_list_item(
            source, row, row_index, header_str
        )

        item.status = (FacilityListItem.PARSED,)
        item.processing_results = [
            {
                'action': ProcessingAction.PARSE,
                'started_at': self.__parsing_started,
                'error': False,
                'finished_at': str(timezone.now()),
                'is_geocoded': False,
            }
        ]
        item.save()

        log.info(f'[API Upload] Source created. Id: {source.id}')
        log.info(f'[API Upload] Source is public: {source.is_public}')
        log.info(f'[API Upload] Source should create: {source.create}')
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
            return self.__handle_extended_field_creation_error(
                exc, item, result
            )

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
            geocode_result = geocode_address(row.address, row.country_code)

            self.__handle_geocode_result(
                geocode_result, item, result, geocode_started
            )

        except Exception as exc:
            self.__handle_geocode_error(
                item, row, geocode_started, result, exc
            )

        if item.status == FacilityListItem.GEOCODED:
            self.__handle_match_process(source, item, result)

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

    def _create_source(self) -> Source:
        return Source.objects.create(
            contributor=self.__contributor,
            source_type=Source.SINGLE,
            is_public=self.__public_submission,
            create=self.__should_create,
        )

    @staticmethod
    def _create_facility_list_item(
        source: Source, row: RowDTO, idx: int, header_str: str
    ) -> FacilityListItem:
        return FacilityListItem.objects.create(
            source=source,
            row_index=idx,
            raw_data=','.join(f'"{value}"' for value in row.raw_json.values()),
            raw_json=row.raw_json,
            raw_header=header_str,
            name=row.name,
            clean_name=row.clean_name,
            address=row.address,
            clean_address=row.clean_address,
            country_code=row.country_code,
            sector=row.sector,
            source_uuid=source
        )

    def __handle_validation_errors(self) -> Response:
        errors = self.__contri_cleaner_processed_data.errors
        log.error(f'[API Upload] CC Validation Errors: {errors}')
        return Response(
            {
                "message": "The provided data could not be processed",
                "errors": errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    @staticmethod
    def __handle_parsing_errors(errors: List[dict]) -> Response:
        log.error(f'[API Upload] CC Parsing Errors: {errors}')
        return Response(
            {
                "message": "The provided data could not be parsed",
                "errors": errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def __handle_extended_field_creation_error(
        self,
        exc: Union[ValidationError, ValueError],
        item: FacilityListItem,
        result: dict,
    ) -> Response:
        error_message = ''

        if isinstance(exc, ValueError):
            error_message = str(exc)
        else:
            error_message = exc.message

        item.status = FacilityListItem.ERROR_PARSING
        item.processing_results.append(
            {
                'action': ProcessingAction.PARSE,
                'started_at': self.__parsing_started,
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
            '[API Upload] Creation of ExtendedField error: ' f'{error_message}'
        )
        log.info(f'[API Upload] FacilityListItem Id: {item.id}')
        return Response(result, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def __handle_geocode_result(
        geocode_result: dict,
        item: FacilityListItem,
        result: dict,
        geocode_started: str,
    ) -> None:
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
            result['message'] = APIErrorMessages.GEOCODED_NO_RESULTS

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

    @staticmethod
    def __handle_geocode_error(
        item: FacilityListItem,
        row: RowDTO,
        geocode_started: str,
        result: dict,
        exc: Exception,
    ) -> Response:
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
        return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def __handle_match_process(
        self, source: Source, item: FacilityListItem, result: Dict[str, Any]
    ) -> None:
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
            fli_temp = FacilityListItemTemp.objects.get(source=source.id)
            if fli_temp.status == FacilityListItemTemp.GEOCODED:
                log.info('[API Upload] Started Match process!')
                log.info(f'[API Upload] FacilityListItem Id: {item.id}')
                log.info(
                    f'[API Upload] FacilityListItemTemp Id: {fli_temp.id}'
                )
                log.info(f'[API Upload] Source Id: {item.id}')
                asyncio.run(produce_message_match_process(source.id))
                break
            asyncio.sleep(1)
            timer = timer + 1

        # Handle results of "match" process from Dedupe Hub
        result = handle_external_match_process_result(
            fli_temp.id, result, self.__request, self.__should_create
        )

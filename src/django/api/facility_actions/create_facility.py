import asyncio
import json
import logging
import traceback

from api.constants import ErrorMessages, FileHeaderField, ProcessingAction
from api.extended_fields import create_extendedfields_for_listitem
from api.geocoding import geocode_address
from api.kafka_producer import produce_message_match_process
from api.models.facility.facility_list_item import FacilityListItem
from api.models.facility.facility_list_item_temp import FacilityListItemTemp
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


class CreateFacility:

    def createApi(request, row, source, should_create):

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
            list(row.fields.keys()), request.user.contributor
        )

        item = FacilityListItem.objects.create(
            source=source,
            row_index=0,
            raw_data=json.dumps(request.data),
            raw_json=row.raw_json,
            raw_header='',
            status=FacilityListItem.PARSED,
            name=row.name,
            clean_name=row.clean_name,
            address=row.address,
            clean_address=row.clean_address,
            country_code=row.country_code,
            sector=row.sector,
            processing_results=[
                {
                    'action': ProcessingAction.PARSE,
                    'started_at': parse_started,
                    'error': False,
                    'finished_at': str(timezone.now()),
                    'is_geocoded': False,
                }
            ],
        )

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
            (item, row.fields)
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
            geocode_result = geocode_address(row.address, row.country_code)
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
                fli_temp.id, result, request, should_create
            )

        errors_status = [
            FacilityListItem.ERROR_MATCHING,
            FacilityListItem.GEOCODED_NO_RESULTS,
        ]

        log.info(f'[API Upload] Result data: {result}')
        log.info(f'[API Upload] FacilityListItem Id: {item.id}')
        log.info(f'[API Upload] Source Id: {item.id}')

        if should_create and result['status'] not in errors_status:
            return Response(result, status=status.HTTP_201_CREATED)
        else:
            return Response(result, status=status.HTTP_200_OK)

    def createList(
        rows, contributor, header_row_keys, header_str, source, serializer
    ):

        parsing_started = str(timezone.now())

        create_nonstandard_fields(header_row_keys, contributor)

        log.info(f'[List Upload] Source created. Id {source.id}!')
        is_geocoded = False
        parsed_items = set()
        for idx, row in enumerate(rows):
            item = FacilityListItem.objects.create(
                row_index=idx,
                raw_data=','.join(row.raw_json.values()),
                raw_json=row.raw_json,
                raw_header=header_str,
                sector=row.sector,
                source=source,
                country_code=row.country_code,
                name=row.name,
                clean_name=row.clean_name,
                address=row.address,
                clean_address=row.clean_address,
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

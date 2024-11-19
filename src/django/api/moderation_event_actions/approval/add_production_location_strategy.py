import logging
from datetime import datetime

from api.models.moderation_event import ModerationEvent
from api.moderation_event_actions.approval.event_approval_strategy import (
    EventApprovalStrategy,
)
from api.models.source import Source
from api.models.facility.facility_list_item import FacilityListItem
from api.models.nonstandard_field import NonstandardField
from api.models.facility.facility import Facility
from api.models.facility.facility_match_temp import FacilityMatchTemp
from api.models.facility.facility_match import FacilityMatch
from api.models.facility.facility_list_item_temp import FacilityListItemTemp
from api.constants import ProcessingAction
from api.extended_fields import create_extendedfields_for_single_item
from api.os_id import make_os_id
from django.utils import timezone
from django.contrib.gis.geos import Point
from rest_framework.response import Response
from django.db import transaction
from rest_framework import status


log = logging.getLogger(__name__)


class AddProductionLocationStrategy(EventApprovalStrategy):
    '''
    Class defines the strategy for processing a moderation event for adding a production location.
    '''

    def __init__(self, moderation_event: ModerationEvent) -> None:
        # self.__moderation_event = moderation_event
        self.__event = moderation_event

    def process_moderation_event(self) -> Response:
        with transaction.atomic():
            data = self.__event.cleaned_data
            log.info(f'[Moderation Event] Processing event with data: {data}')

            contributor = self.__event.contributor
            log.info(f'[Moderation Event] Contributor: {contributor}')

            source = self.__create_source(contributor)
            log.info(f'[Moderation Event] Source created. Id: {source.id}')

            header_row_keys = data["raw_json"].keys()
            self.__create_nonstandard_fields(header_row_keys, contributor)
            log.info('[Moderation Event] Nonstandard fields created.')

            header_str = ','.join(header_row_keys)
            item = self.__create_facility_list_item(
                source, data, header_str, FacilityListItem.MATCHED
            )
            log.info(
                f'[Moderation Event] FacilityListItem created. Id: '
                f'{item.id}'
            )

            create_extendedfields_for_single_item(item, data["fields"])
            log.info('[Moderation Event] Extended fields created.')

            self.__set_geocoded_location(item, data, self.__event)
            log.info('[Moderation Event] Geocoded location set.')

            facility_id = make_os_id(item.country_code)
            log.info(f'[Moderation Event] Facility ID created: {facility_id}')

            self.__create_new_facility(item, facility_id)
            log.info(f'[Moderation Event] Facility created. Id: {facility_id}')

            self.__update_item_with_facility_id_and_processing_results(
                item, facility_id
            )
            log.info(
                '[Moderation Event] FacilityListItem updated with '
                'facility ID.'
            )

            FacilityListItemTemp.copy(item)
            log.info('[Moderation Event] FacilityListItemTemp created.')

            self.__create_facility_match_temp(item)
            log.info('[Moderation Event] FacilityMatchTemp created.')

            self.__create_facility_match(item)
            log.info('[Moderation Event] FacilityMatch created.')

            self.__update_event(self.__event, item)
            log.info(
                '[Moderation Event] Status and os_id of Moderation Event '
                'updated.'
            )

            return Response(
                {"os_id": item.facility_id}, status=status.HTTP_201_CREATED
            )

    @staticmethod
    def __create_source(contributor) -> Source:
        return Source.objects.create(
            contributor=contributor,
            source_type=Source.SINGLE,
            is_public=True,
            create=True,
        )

    @staticmethod
    def __create_nonstandard_fields(fields, contributor):
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

    @staticmethod
    def __set_geocoded_location(item, data, event):
        if event.geocode_result:
            item.geocoded_point = Point(
                event.geocode_result["longitude"],
                event.geocode_result["latitude"],
            )
            item.geocoded_address = event.geocode_result["geocoded_address"]
            item.processing_results.append(
                {
                    'action': ProcessingAction.GEOCODE,
                    'started_at': str(timezone.now()),
                    'error': False,
                    'skipped_geocoder': False,
                    'data': event.geocode_result['full_response'],
                    'finished_at': str(timezone.now()),
                }
            )
        else:
            item.geocoded_point = Point(
                data["fields"]["lng"], data["fields"]["lat"]
            )
            item.processing_results.append(
                {
                    'action': ProcessingAction.GEOCODE,
                    'started_at': str(timezone.now()),
                    'error': False,
                    'skipped_geocoder': True,
                    'finished_at': str(timezone.now()),
                }
            )
        item.save()

    @staticmethod
    def __create_facility_list_item(source, data, header_str, status):
        return FacilityListItem.objects.create(
            source=source,
            row_index=0,
            raw_data=','.join(
                f'"{value}"' for value in data["raw_json"].values()
            ),
            raw_json=data["raw_json"],
            raw_header=header_str,
            name=data["name"],
            clean_name=data["clean_name"],
            address=data["address"],
            clean_address=data["clean_address"],
            country_code=data["country_code"],
            sector=data["sector"],
            status=status,
            processing_results=[
                {
                    'action': ProcessingAction.PARSE,
                    'started_at': str(timezone.now()),
                    'error': False,
                    'finished_at': str(timezone.now()),
                    'is_geocoded': False,
                }
            ],
        )

    @staticmethod
    def __create_new_facility(item, facility_id):
        return Facility.objects.create(
            id=facility_id,
            name=item.name,
            address=item.address,
            country_code=item.country_code,
            location=item.geocoded_point,
            created_from_id=item.id,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

    @staticmethod
    def __update_item_with_facility_id_and_processing_results(
        item, facility_id
    ):
        item.facility_id = facility_id
        item.processing_results.append(
            {
                'action': ProcessingAction.MATCH,
                'started_at': str(timezone.now()),
                'error': False,
                'finished_at': str(timezone.now()),
            }
        )
        item.save()

    @staticmethod
    def __create_facility_match_temp(item):
        return FacilityMatchTemp.objects.create(
            facility_id=item.facility_id,
            confidence=1.0,
            facility_list_item_id=item.id,
            status=FacilityMatchTemp.AUTOMATIC,
            results={"match_type": "moderation_event"},
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

    @staticmethod
    def __create_facility_match(item):
        return FacilityMatch.objects.create(
            facility_id=item.facility_id,
            confidence=1.0,
            facility_list_item_id=item.id,
            status=FacilityMatch.AUTOMATIC,
            results={"match_type": "moderation_event"},
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

    @staticmethod
    def __update_event(event, item):
        event.status = ModerationEvent.Status.APPROVED
        event.os_id = item.facility_id
        event.save()

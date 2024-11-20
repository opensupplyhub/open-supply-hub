import logging
from datetime import datetime

from typing import Dict, List, Type, Union

from django.contrib.gis.geos import Point
from django.db import transaction
from django.utils import timezone

from api.constants import ProcessingAction
from api.extended_fields import create_extendedfields_for_single_item
from api.models.contributor.contributor import Contributor
from api.models.facility.facility import Facility
from api.models.facility.facility_list_item import FacilityListItem
from api.models.facility.facility_list_item_temp import FacilityListItemTemp
from api.models.facility.facility_match import FacilityMatch
from api.models.facility.facility_match_temp import FacilityMatchTemp
from api.models.moderation_event import ModerationEvent
from api.models.nonstandard_field import NonstandardField
from api.models.source import Source
from api.moderation_event_actions.approval.event_approval_strategy import (
    EventApprovalStrategy,
)
from api.os_id import make_os_id


log = logging.getLogger(__name__)


class AddProductionLocationStrategy(EventApprovalStrategy):
    '''
    Class defines the strategy for processing a moderation event for adding a
    production location.
    '''

    def __init__(self, moderation_event: ModerationEvent) -> None:
        self.__event = moderation_event

    def process_moderation_event(self) -> FacilityListItem:
        with transaction.atomic():
            data: Dict = self.__event.cleaned_data
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
                '[Moderation Event] FacilityListItem updated with facility ID.'
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

            return item

    @staticmethod
    def __create_source(contributor: Contributor) -> Source:
        return Source.objects.create(
            contributor=contributor,
            source_type=Source.SINGLE,
            is_public=True,
            create=True,
        )

    @staticmethod
    def __create_nonstandard_fields(
        fields: List[str], contributor: Contributor
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

    @staticmethod
    def __create_facility_list_item(
        source: Source, data: Dict, header_str: str, status: str
    ) -> FacilityListItem:
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

    def __set_geocoded_location(
        self, item: FacilityListItem, data: Dict, event: ModerationEvent
    ) -> None:
        geocode_result = event.geocode_result
        fields = data["fields"]

        if geocode_result:
            self.__apply_geocode_result(item, geocode_result)

        else:
            self.__apply_manual_location(item, fields)

        item.save()

    @staticmethod
    def __apply_geocode_result(
        item: FacilityListItem, geocode_result: Dict
    ) -> None:
        item.geocoded_point = Point(
            geocode_result["longitude"], geocode_result["latitude"]
        )
        item.geocoded_address = geocode_result["geocoded_address"]
        item.processing_results.append(
            {
                "action": ProcessingAction.GEOCODE,
                "started_at": str(timezone.now()),
                "error": False,
                "skipped_geocoder": False,
                "data": geocode_result["full_response"],
                "finished_at": str(timezone.now()),
            }
        )

    @staticmethod
    def __apply_manual_location(item: FacilityListItem, fields: Dict) -> None:
        item.geocoded_point = Point(fields["lng"], fields["lat"])
        item.processing_results.append(
            {
                "action": ProcessingAction.GEOCODE,
                "started_at": str(timezone.now()),
                "error": False,
                "skipped_geocoder": True,
                "finished_at": str(timezone.now()),
            }
        )

    @staticmethod
    def __create_new_facility(
        item: FacilityListItem, facility_id: str
    ) -> Facility:
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
        item: FacilityListItem, facility_id: str
    ) -> None:
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

    def __create_facility_match_temp(
        self, item: FacilityListItem
    ) -> FacilityMatchTemp:
        return self.__create_facility_match_record(
            model=FacilityMatchTemp,
            item=item,
            status=FacilityMatchTemp.AUTOMATIC,
        )

    def __create_facility_match(self, item: FacilityListItem) -> FacilityMatch:
        return self.__create_facility_match_record(
            model=FacilityMatch,
            item=item,
            status=FacilityMatch.AUTOMATIC,
        )

    @staticmethod
    def __create_facility_match_record(
        model: Union[Type[FacilityMatchTemp], Type[FacilityMatch]],
        item: FacilityListItem,
        status: str,
    ) -> Union[FacilityMatchTemp, FacilityMatch]:
        return model.objects.create(
            facility_id=item.facility_id,
            confidence=1.0,
            facility_list_item_id=item.id,
            status=status,
            results={"match_type": "moderation_event"},
            created_at=timezone.now(),
            updated_at=timezone.now(),
        )

    @staticmethod
    def __update_event(event: ModerationEvent, item: FacilityListItem) -> None:
        event.status = ModerationEvent.Status.APPROVED
        event.os_id = item.facility_id
        event.save()

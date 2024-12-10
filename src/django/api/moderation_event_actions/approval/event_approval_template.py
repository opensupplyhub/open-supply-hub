import logging
from abc import ABC, abstractmethod
from typing import Dict, KeysView, Type, Union

from django.contrib.gis.geos import Point
from django.db import transaction
from django.utils import timezone

from api.constants import ProcessingAction
from api.extended_fields import create_extendedfields_for_single_item
from api.models.contributor.contributor import Contributor
from api.models.extended_field import ExtendedField
from api.models.facility.facility_list_item import FacilityListItem
from api.models.facility.facility_list_item_temp import FacilityListItemTemp
from api.models.facility.facility_match import FacilityMatch
from api.models.facility.facility_match_temp import FacilityMatchTemp
from api.models.moderation_event import ModerationEvent
from api.models.source import Source
from api.views.fields.create_nonstandard_fields import (
    create_nonstandard_fields,
)

log = logging.getLogger(__name__)


class EventApprovalTemplate(ABC):
    """
    A template method class that defines the overall steps for processing
    a moderation event. Subclasses provide the specifics by overriding
    abstract methods and hooks.
    """

    def __init__(self, moderation_event: ModerationEvent) -> None:
        self.__event = moderation_event

    def process_moderation_event(self) -> FacilityListItem:
        with transaction.atomic():
            data: Dict = self.__event.cleaned_data
            log.info(f'[Moderation Event] Processing event with data: {data}')

            contributor: Contributor = self.__event.contributor
            log.info(f'[Moderation Event] Contributor: {contributor}')

            source: Source = self.__create_source(contributor)
            log.info(f'[Moderation Event] Source created. Id: {source.id}')

            header_row_keys: KeysView[str] = data["raw_json"].keys()
            create_nonstandard_fields(header_row_keys, contributor)
            log.info('[Moderation Event] Nonstandard fields created.')

            header_str: str = ','.join(header_row_keys)
            item: FacilityListItem = self.__create_facility_list_item(
                source, data, header_str, FacilityListItem.MATCHED
            )
            log.info(
                '[Moderation Event] FacilityListItem created. Id: '
                f'{item.id}'
            )

            create_extendedfields_for_single_item(item, data["fields"])
            log.info('[Moderation Event] Extended fields created.')

            self.__set_geocoded_location(item, data, self.__event)
            log.info('[Moderation Event] Geocoded location set.')

            facility_id = self._get_os_id(item.country_code)

            self._create_new_facility(item, facility_id)

            self.__update_item_with_facility_id_and_processing_results(
                item, facility_id
            )
            log.info(
                '[Moderation Event] FacilityListItem updated with facility ID.'
            )

            self.__create_list_item_temp(item)
            log.info('[Moderation Event] FacilityListItemTemp created.')

            self.__update_extended_fields(item)
            log.info(
                '[Moderation Event] Extended fields updated with facility ID.'
            )

            self.__create_facility_match_temp(item)
            log.info('[Moderation Event] FacilityMatchTemp created.')

            self.__create_facility_match(item)
            log.info('[Moderation Event] FacilityMatch created.')

            self._update_event(self.__event, item)
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
            geocode_result["geocoded_point"]["lng"],
            geocode_result["geocoded_point"]["lat"],
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

    @staticmethod
    def __create_list_item_temp(item: FacilityListItem) -> None:
        FacilityListItemTemp.copy(item)

    @staticmethod
    def __update_extended_fields(item: FacilityListItem) -> None:
        extended_fields = ExtendedField.objects.filter(
            facility_list_item=item.id
        )
        for field in extended_fields:
            field.facility_id = item.facility_id
            field.save()

    def __create_facility_match_temp(self, item: FacilityListItem) -> None:
        self.__create_facility_match_record(
            model=FacilityMatchTemp,
            item=item,
        )

    def __create_facility_match(self, item: FacilityListItem) -> None:
        self.__create_facility_match_record(
            model=FacilityMatch,
            item=item,
        )

    def __create_facility_match_record(
        self,
        model: Union[Type[FacilityMatchTemp], Type[FacilityMatch]],
        item: FacilityListItem,
    ) -> None:
        match_type = self._get_match_type()

        model.objects.create(
            facility_id=item.facility_id,
            confidence=1.0,
            facility_list_item_id=item.id,
            status=FacilityMatch.AUTOMATIC,
            results={"match_type": match_type},
            created_at=timezone.now(),
            updated_at=timezone.now(),
        )

    @staticmethod
    def _update_event(event: ModerationEvent, item: FacilityListItem) -> None:
        event.status = ModerationEvent.Status.APPROVED
        event.os_id = item.facility_id
        event.save()

    @abstractmethod
    def _get_os_id(self, country_code: str) -> str:
        """Return the os_id."""
        raise NotImplementedError

    @abstractmethod
    def _get_match_type(self) -> str:
        """
        Return the match_type that should be used when creating
        facility matches.
        """
        raise NotImplementedError

    @staticmethod
    def _create_new_facility(item: FacilityListItem, facility_id: str) -> None:
        """Hook method to create a new facility."""
        pass

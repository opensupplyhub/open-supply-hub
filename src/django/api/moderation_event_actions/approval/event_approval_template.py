import logging
from abc import ABC, abstractmethod
from typing import Dict, KeysView, Type, Union

from django.contrib.gis.geos import Point
from django.db import transaction
from django.utils import timezone

from api.constants import (
    LOCATION_CONTRIBUTION_APPROVAL_LOG_PREFIX,
    ProcessingAction,
)
from api.extended_fields import (
    create_extendedfields_for_single_item,
    create_partner_extendedfields_for_single_item,
    update_extendedfields_for_list_item,
)
from api.models.contributor.contributor import Contributor
from api.models.facility.facility_list_item import FacilityListItem
from api.models.facility.facility_list_item_temp import FacilityListItemTemp
from api.models.facility.facility_match import FacilityMatch
from api.models.facility.facility_match_temp import FacilityMatchTemp
from api.models.moderation_event import ModerationEvent
from api.models.source import Source
from api.models.user import User
from api.views.fields.create_nonstandard_fields import (
    create_nonstandard_fields,
)

log = logging.getLogger(__name__)


class EventApprovalTemplate(ABC):
    """
    A template method class that defines the overall steps for processing
    approval-type moderation event actions. It could be applied only for
    creating a new production location or adding an additional contribution to
    an existing production location.
    Subclasses provide the specifics by overriding
    abstract methods and hooks.
    """

    def __init__(
        self,
        moderation_event: ModerationEvent,
        moderator: User
    ) -> None:
        self.__event = moderation_event
        self.__moderator = moderator

    @transaction.atomic
    def process_moderation_event(self) -> FacilityListItem:
        data: Dict = self.__event.cleaned_data
        log.info(
            f'{LOCATION_CONTRIBUTION_APPROVAL_LOG_PREFIX} Processing event '
            f'with data: {data}'
        )

        contributor: Contributor = self.__event.contributor
        log.info(
            f'{LOCATION_CONTRIBUTION_APPROVAL_LOG_PREFIX} Contributor: '
            f'{contributor}'
        )

        source: Source = self.__create_source(contributor)
        log.info(
            f'{LOCATION_CONTRIBUTION_APPROVAL_LOG_PREFIX} Source created. '
            f'Id: {source.id}'
        )

        header_row_keys: KeysView[str] = data["raw_json"].keys()
        create_nonstandard_fields(header_row_keys, contributor)
        log.info(
            f'{LOCATION_CONTRIBUTION_APPROVAL_LOG_PREFIX} Nonstandard fields '
            'created.'
        )

        header_str: str = ','.join(header_row_keys)
        item: FacilityListItem = self.__create_facility_list_item(
            source, data, header_str
        )
        log.info(
            f'{LOCATION_CONTRIBUTION_APPROVAL_LOG_PREFIX} FacilityListItem '
            f'created. Id: {item.id}'
        )

        create_extendedfields_for_single_item(
            item,
            data["fields"]
        )
        log.info(
            f'{LOCATION_CONTRIBUTION_APPROVAL_LOG_PREFIX} Extended fields '
            'created.'
        )

        create_partner_extendedfields_for_single_item(
            item,
            data["fields"]
        )
        log.info(
            f'{LOCATION_CONTRIBUTION_APPROVAL_LOG_PREFIX} Partner extended '
            'fields created.'
        )

        self.__set_geocoded_location(item, data, self.__event)
        log.info(
            f'{LOCATION_CONTRIBUTION_APPROVAL_LOG_PREFIX} Geocoded '
            'location set.'
        )

        facility_id = self._get_os_id(item.country_code)

        self._create_new_facility(item, facility_id)

        self.__update_item_with_facility_id_and_processing_results(
            item, facility_id
        )
        log.info(
            f'{LOCATION_CONTRIBUTION_APPROVAL_LOG_PREFIX} FacilityListItem '
            'updated with facility ID.'
        )

        self.__create_list_item_temp(item)
        log.info(
            f'{LOCATION_CONTRIBUTION_APPROVAL_LOG_PREFIX} '
            'FacilityListItemTemp created.'
        )

        update_extendedfields_for_list_item(item)
        log.info(
            f'{LOCATION_CONTRIBUTION_APPROVAL_LOG_PREFIX} Extended fields '
            'updated with facility ID.'
        )

        self.__create_facility_match_temp(item)
        log.info(
            f'{LOCATION_CONTRIBUTION_APPROVAL_LOG_PREFIX} FacilityMatchTemp '
            'created.'
        )

        self.__create_facility_match(item)
        log.info(
            f'{LOCATION_CONTRIBUTION_APPROVAL_LOG_PREFIX} FacilityMatch '
            'created.'
        )

        self.__update_event(item)
        log.info(
            f'{LOCATION_CONTRIBUTION_APPROVAL_LOG_PREFIX} Status and os_id of '
            'Moderation Event updated.'
        )

        self._update_facility_updated_at(item.facility.id)

        return item

    @staticmethod
    def __create_source(contributor: Contributor) -> Source:
        return Source.objects.create(
            contributor=contributor,
            source_type=Source.SINGLE,
            is_public=True,
            create=True,
        )

    def __create_facility_list_item(
        self, source: Source, data: Dict, header_str: str
    ) -> FacilityListItem:
        status = self._get_facilitylistitem_status()

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

        if geocode_result:
            self.__apply_geocode_result(item, geocode_result)
        else:
            lat = data["fields"]["lat"]
            lng = data["fields"]["lng"]
            self.__apply_manual_location(item, lat, lng)

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
    def __apply_manual_location(
        item: FacilityListItem, lat: float, lng: float
    ) -> None:
        item.geocoded_point = Point(lng, lat)
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

    def __create_facility_match_temp(self, item: FacilityListItem) -> None:
        self.__create_facility_match_record(
            model=FacilityMatchTemp,
            item=item,
        )

    def __create_facility_match(self, item: FacilityListItem) -> None:
        self.__create_facility_match_record(model=FacilityMatch, item=item)

    def __create_facility_match_record(
        self,
        model: Union[Type[FacilityMatchTemp], Type[FacilityMatch]],
        item: FacilityListItem,
    ) -> None:
        match_type = self._get_match_type()
        status = self._get_match_status()

        model.objects.create(
            facility_id=item.facility_id,
            confidence=1.0,
            facility_list_item_id=item.id,
            status=status,
            results={"match_type": match_type},
            created_at=timezone.now(),
            updated_at=timezone.now(),
        )

    def __update_event(self, item: FacilityListItem) -> None:
        event = self.__event
        event.status = ModerationEvent.Status.APPROVED
        event.status_change_date = timezone.now()
        event.action_type = self._get_action_type()
        event.action_perform_by = self.__moderator
        event.os_id = item.facility_id
        event.save()

    @abstractmethod
    def _get_os_id(self, country_code: str) -> str:
        """Return the os_id."""
        raise NotImplementedError

    @abstractmethod
    def _get_facilitylistitem_status(self) -> str:
        """
        Return the status that should be used when creating
        facility list items.
        """
        raise NotImplementedError

    @abstractmethod
    def _get_match_type(self) -> str:
        """
        Return the match_type that should be used when creating
        facility matches.
        """
        raise NotImplementedError

    @abstractmethod
    def _get_match_status(self) -> str:
        """
        Return the status that should be used when creating
        facility matches.
        """
        raise NotImplementedError

    @abstractmethod
    def _get_action_type(self) -> str:
        """
        Return the action type that should be used when
        updating the moderation event.
        """
        raise NotImplementedError

    @staticmethod
    def _create_new_facility(item: FacilityListItem, facility_id: str) -> None:
        """Hook method to create a new facility."""
        pass

    @staticmethod
    def _update_facility_updated_at(facility_id: str) -> None:
        """Hook method to update a facility updated_at field."""
        pass

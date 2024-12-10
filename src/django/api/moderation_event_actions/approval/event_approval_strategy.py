from abc import ABC, abstractmethod
from typing import Dict, Type, Union

from django.utils import timezone
from django.contrib.gis.geos import Point

from api.constants import ProcessingAction
from api.models.extended_field import ExtendedField
from api.models.facility.facility_list_item import FacilityListItem
from api.models.facility.facility_match_temp import FacilityMatchTemp
from api.models.facility.facility_match import FacilityMatch
from api.models.contributor.contributor import Contributor
from api.models.moderation_event import ModerationEvent
from api.models.source import Source


class EventApprovalStrategy(ABC):
    '''
    Abstract class for approval moderation event strategies.
    '''

    @abstractmethod
    def process_moderation_event(self) -> FacilityListItem:
        '''
        Abstract method to process a moderation event.
        '''
        pass

    @staticmethod
    def _create_source(contributor: Contributor) -> Source:
        return Source.objects.create(
            contributor=contributor,
            source_type=Source.SINGLE,
            is_public=True,
            create=True,
        )

    @staticmethod
    def _create_facility_list_item(
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

    def _set_geocoded_location(
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
    def _update_item_with_facility_id_and_processing_results(
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
    def _update_extended_fields(item: FacilityListItem) -> None:
        extended_fields = ExtendedField.objects.filter(
            facility_list_item=item.id
        )
        for field in extended_fields:
            field.facility_id = item.facility_id
            field.save()

    def _create_facility_match_temp(
        self, item: FacilityListItem, match_type: str
    ) -> FacilityMatchTemp:
        return self.__create_facility_match_record(
            model=FacilityMatchTemp,
            item=item,
            status=FacilityMatchTemp.AUTOMATIC,
            match_type=match_type,
        )

    def _create_facility_match(
            self, item: FacilityListItem, match_type: str
    ) -> FacilityMatch:
        return self.__create_facility_match_record(
            model=FacilityMatch,
            item=item,
            status=FacilityMatch.AUTOMATIC,
            match_type=match_type,
        )

    @staticmethod
    def __create_facility_match_record(
        model: Union[Type[FacilityMatchTemp], Type[FacilityMatch]],
        item: FacilityListItem,
        status: str,
        match_type: str
    ) -> Union[FacilityMatchTemp, FacilityMatch]:
        return model.objects.create(
            facility_id=item.facility_id,
            confidence=1.0,
            facility_list_item_id=item.id,
            status=status,
            results={"match_type": f"moderation_event - {match_type}"},
            created_at=timezone.now(),
            updated_at=timezone.now(),
        )

    @staticmethod
    def _update_event(event: ModerationEvent, item: FacilityListItem) -> None:
        event.status = ModerationEvent.Status.APPROVED
        event.os_id = item.facility_id
        event.save()

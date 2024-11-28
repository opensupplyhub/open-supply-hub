import logging
from typing import Dict, KeysView

from django.db import transaction

from api.extended_fields import create_extendedfields_for_single_item
from api.models.contributor.contributor import Contributor
from api.models.facility.facility_list_item import FacilityListItem
from api.models.facility.facility_list_item_temp import FacilityListItemTemp
from api.models.moderation_event import ModerationEvent
from api.models.source import Source
from api.moderation_event_actions.approval.event_approval_strategy import (
    EventApprovalStrategy,
)
from api.views.fields.create_nonstandard_fields import (
    create_nonstandard_fields,
)


log = logging.getLogger(__name__)


class UpdateProductionLocationStrategy(EventApprovalStrategy):
    def __init__(self, moderation_event: ModerationEvent, os_id: str) -> None:
        self.__event = moderation_event
        self.__os_id = os_id

    def process_moderation_event(self) -> FacilityListItem:
        with transaction.atomic():
            data: Dict = self.__event.cleaned_data
            log.info(f'[Moderation Event] Processing event with data: {data}')

            contributor: Contributor = self.__event.contributor
            log.info(f'[Moderation Event] Contributor: {contributor}')

            source: Source = self._create_source(contributor)
            log.info(f'[Moderation Event] Source created. Id: {source.id}')

            header_row_keys: KeysView[str] = data["raw_json"].keys()
            create_nonstandard_fields(header_row_keys, contributor)
            log.info('[Moderation Event] Nonstandard fields created.')

            header_str: str = ','.join(header_row_keys)
            item: FacilityListItem = self._create_facility_list_item(
                source, data, header_str, FacilityListItem.MATCHED
            )
            log.info(
                f'[Moderation Event] FacilityListItem created. Id: '
                f'{item.id}'
            )

            create_extendedfields_for_single_item(item, data["fields"])
            log.info('[Moderation Event] Extended fields created.')

            self._set_geocoded_location(item, data, self.__event)
            log.info('[Moderation Event] Geocoded location set.')

            self._update_item_with_facility_id_and_processing_results(
                item, self.__os_id
            )
            log.info(
                '[Moderation Event] FacilityListItem updated with facility ID.'
            )

            FacilityListItemTemp.copy(item)
            log.info('[Moderation Event] FacilityListItemTemp created.')

            self._update_extended_fields(item)
            log.info(
                '[Moderation Event] Extended fields updated with facility ID.'
            )

            self._create_facility_match_temp(
                item, FacilityListItem.CONFIRMED_MATCH
            )
            log.info('[Moderation Event] FacilityMatchTemp created.')

            self._create_facility_match(item, FacilityListItem.CONFIRMED_MATCH)
            log.info('[Moderation Event] FacilityMatch created.')

            self._update_event(self.__event, item)
            log.info(
                '[Moderation Event] Status and os_id of Moderation Event '
                'updated.'
            )

            return item

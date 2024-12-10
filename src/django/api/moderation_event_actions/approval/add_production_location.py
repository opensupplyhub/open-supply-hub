import logging
from datetime import datetime

from api.constants import APIV1MatchTypes
from api.models.facility.facility import Facility
from api.models.facility.facility_list_item import FacilityListItem
from api.models.moderation_event import ModerationEvent
from api.moderation_event_actions.approval.event_approval_template import (
    EventApprovalTemplate,
)
from api.os_id import make_os_id

log = logging.getLogger(__name__)


class AddProductionLocation(EventApprovalTemplate):
    def __init__(self, moderation_event: ModerationEvent) -> None:
        super().__init__(moderation_event)

    def _get_os_id(self, country_code: str) -> str:
        os_id = make_os_id(country_code)
        log.info(f'[Moderation Event] OS ID was generated: {os_id}')

        return os_id

    def _get_match_type(self) -> str:
        return APIV1MatchTypes.NEW_PRODUCTION_LOCATION

    @staticmethod
    def _create_new_facility(item: FacilityListItem, facility_id: str) -> None:
        Facility.objects.create(
            id=facility_id,
            name=item.name,
            address=item.address,
            country_code=item.country_code,
            location=item.geocoded_point,
            created_from_id=item.id,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        log.info(f'[Moderation Event] Facility created. Id: {facility_id}')

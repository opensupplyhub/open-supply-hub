import logging

from django.utils import timezone

from api.constants import (
    LOCATION_CONTRIBUTION_APPROVAL_LOG_PREFIX,
    APIV1MatchTypes,
)
from api.models.facility.facility import Facility
from api.models.facility.facility_list_item import FacilityListItem
from api.models.facility.facility_match import FacilityMatch
from api.models.moderation_event import ModerationEvent
from api.models.user import User
from api.moderation_event_actions.approval.event_approval_template import (
    EventApprovalTemplate,
)
from api.os_id import make_os_id

log = logging.getLogger(__name__)


class AddProductionLocation(EventApprovalTemplate):
    def __init__(
        self,
        moderation_event: ModerationEvent,
        moderator: User
    ) -> None:
        super().__init__(moderation_event, moderator)

    def _get_os_id(self, country_code: str) -> str:
        os_id = make_os_id(country_code)
        log.info(
            f'{LOCATION_CONTRIBUTION_APPROVAL_LOG_PREFIX} OS ID was '
            f'generated: {os_id}'
        )

        return os_id

    def _get_facilitylistitem_status(self) -> str:
        return FacilityListItem.MATCHED

    def _get_match_type(self) -> str:
        return APIV1MatchTypes.NEW_PRODUCTION_LOCATION

    def _get_match_status(self) -> str:
        return FacilityMatch.AUTOMATIC

    def _get_action_type(self):
        return ModerationEvent.ActionType.NEW_LOCATION

    @staticmethod
    def _create_new_facility(item: FacilityListItem, facility_id: str) -> None:
        Facility.objects.create(
            id=facility_id,
            name=item.name,
            address=item.address,
            country_code=item.country_code,
            location=item.geocoded_point,
            created_from_id=item.id,
            created_at=timezone.now(),
            updated_at=timezone.now(),
        )
        log.info(
            f'{LOCATION_CONTRIBUTION_APPROVAL_LOG_PREFIX} Facility created. '
            f'Id: {facility_id}'
        )

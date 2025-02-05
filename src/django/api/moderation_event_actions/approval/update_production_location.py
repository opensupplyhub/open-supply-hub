import logging

from api.constants import (
    LOCATION_CONTRIBUTION_APPROVAL_LOG_PREFIX,
    APIV1MatchTypes,
)
from api.models.facility.facility_list_item import FacilityListItem
from api.models.facility.facility_match import FacilityMatch
from api.models.moderation_event import ModerationEvent
from api.models.user import User
from api.moderation_event_actions.approval.event_approval_template import (
    EventApprovalTemplate,
)

log = logging.getLogger(__name__)


class UpdateProductionLocation(EventApprovalTemplate):
    def __init__(self,
                 moderation_event: ModerationEvent,
                 moderator: User,
                 os_id: str
    ) -> None:
        super().__init__(moderation_event, moderator)
        self.__os_id = os_id

    def _get_os_id(self, _) -> str:
        log.info(
            f'{LOCATION_CONTRIBUTION_APPROVAL_LOG_PREFIX} OS ID received from '
            f'request: {self.__os_id}'
        )
        return self.__os_id

    def _get_facilitylistitem_status(self) -> str:
        return FacilityListItem.CONFIRMED_MATCH

    def _get_match_type(self) -> str:
        return APIV1MatchTypes.CONFIRMED_MATCH

    def _get_match_status(self) -> str:
        return FacilityMatch.CONFIRMED

    def _get_action_type(self):
        return ModerationEvent.ActionType.MATCHED

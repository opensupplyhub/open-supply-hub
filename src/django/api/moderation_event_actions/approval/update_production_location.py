import logging

from api.constants import APIV1MatchTypes
from api.models.moderation_event import ModerationEvent
from api.moderation_event_actions.approval.event_approval_template import (
    EventApprovalTemplate,
)

log = logging.getLogger(__name__)


class UpdateProductionLocation(EventApprovalTemplate):
    def __init__(self, moderation_event: ModerationEvent, os_id: str) -> None:
        super().__init__(moderation_event)
        self.__os_id = os_id

    def _get_os_id(self, _) -> str:
        log.info(
            f'[Moderation Event] OS ID received from request: {self.__os_id}'
        )
        return self.__os_id

    def _get_match_type(self) -> str:
        return APIV1MatchTypes.CONFIRMED_MATCH

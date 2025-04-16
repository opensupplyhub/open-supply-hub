from __future__ import annotations
from abc import ABC, abstractmethod
import logging

from rest_framework import status

from api.moderation_event_actions.creation.dtos.create_moderation_event_dto \
    import CreateModerationEventDTO
from api.constants import APIV1CommonErrorMessages

log = logging.getLogger(__name__)


class ContributionProcessor(ABC):
    '''
    The class that defines the common interface for location contribution
    processors. Essentially, it is used to implement the Chain of
    Responsibility pattern, allowing the graceful stopping of moderation event
    data processing in case an error occurs, or allowing the entire chain of
    processors to run through in case of a successful pass.
    '''

    _next: ContributionProcessor = None

    def set_next(self, next: ContributionProcessor) -> None:
        self._next = next

    @abstractmethod
    def process(
            self,
            event_dto: CreateModerationEventDTO) -> CreateModerationEventDTO:
        if self._next:
            return self._next.process(event_dto)

        log.error(
            ('[API V1 Location Upload] Internal Moderation Event Creation '
             'Error: The non-existing next handler for processing the '
             'moderation event creation related to location contribution was '
             'called in the last handler of the chain.')
        )
        event_dto.errors = {
            'detail': APIV1CommonErrorMessages.COMMON_INTERNAL_ERROR
        }
        event_dto.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

        return event_dto

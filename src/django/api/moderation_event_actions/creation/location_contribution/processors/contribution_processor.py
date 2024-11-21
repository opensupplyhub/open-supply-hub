from __future__ import annotations
from abc import ABC, abstractmethod

from api.moderation_event_actions.creation.dtos.create_moderation_event_dto \
    import CreateModerationEventDTO


class ContributionProcessor(ABC):
    '''
    The class that defines the common interface for location contribution
    processors. Essentially, it is used to implement the Chain of
    Responsibility pattern, allowing the graceful stopping of moderation event
    data processing in case an error occurs, or allowing the entire chain of
    processors to run through in case of a successful pass.
    '''

    _next: ContributionProcessor = None

    def set_next(self, next: ContributionProcessor):
        self._next = next

    @abstractmethod
    def process(
            self,
            event_dto: CreateModerationEventDTO) -> CreateModerationEventDTO:
        if self._next:
            return self._next.process(event_dto)

        # TODO: return object with the error. I think it is better error
        #       object in DTO which keeps both error code and object
        #       with errors itself
        raise None

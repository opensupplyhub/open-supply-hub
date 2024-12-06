from abc import ABC, abstractmethod

from api.moderation_event_actions.creation.dtos.create_moderation_event_dto \
    import CreateModerationEventDTO


class EventCreationStrategy(ABC):
    @abstractmethod
    def serialize(
            self,
            event_dto: CreateModerationEventDTO) -> CreateModerationEventDTO:
        pass

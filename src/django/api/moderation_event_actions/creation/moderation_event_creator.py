from typing import Dict

from api.moderation_event_actions.creation.event_creation_strategy import (
    EventCreationStrategy
)
from api.moderation_event_actions.creation.dtos.create_moderation_event_dto \
    import CreateModerationEventDTO


class ModerationEventCreator:
    def __init__(self, strategy: EventCreationStrategy) -> None:
        self.__strategy = strategy

    def perform_event_creation(self, event_data: Dict):
        event_dto = CreateModerationEventDTO(raw_data=event_data)
        processed_event = self.__strategy.serialize(event_dto)
        return processed_event

from typing import Dict

from api.moderation_event_actions.creation.event_creation_strategy import (
    EventCreationStrategy
)


class ModerationEventCreator:
    def __init__(self, strategy: EventCreationStrategy) -> None:
        self.__strategy = strategy

    def perform_event_creation(self, moderation_event_data):
        processed_event = self.__strategy.serialize(moderation_event_data)
        return processed_event

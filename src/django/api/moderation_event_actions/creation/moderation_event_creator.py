from api.moderation_event_actions.creation.event_creation_strategy import (
    EventCreationStrategy
)
from api.moderation_event_actions.creation.dtos.create_moderation_event_dto \
    import CreateModerationEventDTO
from api.models.moderation_event import ModerationEvent


class ModerationEventCreator:
    def __init__(self, strategy: EventCreationStrategy) -> None:
        self.__strategy = strategy

    def perform_event_creation(
            self,
            event_dto: CreateModerationEventDTO
            ) -> CreateModerationEventDTO:
        processed_event = self.__strategy.serialize(event_dto)

        if processed_event.errors:
            return event_dto

        event_dto.moderation_event = ModerationEvent.objects.create(
            contributor=processed_event.contributor,
            request_type=processed_event.request_type,
            raw_data=processed_event.raw_data,
            cleaned_data=processed_event.cleaned_data,
            geocode_result=processed_event.geocode_result,
            source=processed_event.source,
            os=processed_event.os
        )

        return event_dto

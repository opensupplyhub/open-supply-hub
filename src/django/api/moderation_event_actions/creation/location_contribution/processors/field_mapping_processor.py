from typing import Dict

from api.moderation_event_actions.creation.location_contribution \
    .processors.contribution_processor import ContributionProcessor
from api.moderation_event_actions.creation.dtos.create_moderation_event_dto \
    import CreateModerationEventDTO


class FieldMappingProcessor(ContributionProcessor):

    def process(self, event: Dict) -> CreateModerationEventDTO:

        if not serializer.is_valid():
            transformed_errors = self.__transform_serializer_errors(
                serializer.errors
            )
            return CreateModerationEventDTO(errors=transformed_errors)

        return super().process(event)
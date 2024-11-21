from typing import Dict

from api.moderation_event_actions.creation.location_contribution \
    .processors.contribution_processor import ContributionProcessor
from api.moderation_event_actions.creation.dtos.create_moderation_event_dto \
    import CreateModerationEventDTO
from api.moderation_event_actions.constants import COMMON_REQ_BODY_ERROR
from api.serializers.v1.contribution_moderation_event_source_field_serializer \
    import ContributionModerationEventSourceFieldSerializer


class SourceProcessor(ContributionProcessor):

    def process(
            self,
            event_dto: CreateModerationEventDTO) -> CreateModerationEventDTO:
        serializer = ContributionModerationEventSourceFieldSerializer(
            data=event_dto.raw_data
        )
        if not serializer.is_valid():
            transformed_errors = self.__transform_serializer_errors(
                serializer.errors
            )
            event_dto.errors = transformed_errors
            return event_dto

        event_dto.source = event_dto.raw_data['source']

        return super().process(event_dto)

    @staticmethod
    def __transform_serializer_errors(serializer_errors: Dict) -> Dict:
        validation_errors = {
            'detail': COMMON_REQ_BODY_ERROR,
            'errors': []
        }

        for field, field_errors in serializer_errors.items():
            for field_error in field_errors:
                validation_errors['errors'].append(
                    {
                        'field': field,
                        'detail': str(field_error)
                    }
                )

        return validation_errors

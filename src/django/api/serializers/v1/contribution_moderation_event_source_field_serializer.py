from rest_framework.serializers import (
    CharField,
    Serializer,
)
from rest_framework.exceptions import ValidationError

from api.models.moderation_event import ModerationEvent


class ContributionModerationEventSourceFieldSerializer(Serializer):
    source = CharField(
        default=ModerationEvent.Source.API.value,
        max_length=3,
        min_length=1,
        trim_whitespace=False
    )

    def validate_source(self, value: str) -> str:
        '''
        Check that the source value is valid according to the source field
        in the ModerationEvent model.
        '''
        source_values = ModerationEvent.Source.values
        is_valid_source = value in source_values
        if not is_valid_source:
            stringified_source_values = ', '.join(source_values)
            raise ValidationError(
                (f'The source value should be one of the following: '
                 f'{stringified_source_values}.')
            )

        return value

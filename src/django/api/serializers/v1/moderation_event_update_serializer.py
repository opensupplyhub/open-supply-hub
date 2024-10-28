from rest_framework.serializers import (
    ModelSerializer,
    ValidationError
)
from api.models.moderation_event \
    import ModerationEvent


class ModerationEventUpdateSerializer(ModelSerializer):

    class Meta:
        model = ModerationEvent
        fields = ['status']

    def validate_status(self, value):
        if value not in [ModerationEvent.Status.PENDING, ModerationEvent.Status.RESOLVED]:
            raise ValidationError("Invalid status.")
        return value
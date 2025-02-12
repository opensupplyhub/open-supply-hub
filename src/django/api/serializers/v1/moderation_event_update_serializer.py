from rest_framework.serializers import (
    ModelSerializer,
    ValidationError,
    CharField,
    IntegerField
)
from rest_framework.fields import empty
from api.models.moderation_event \
    import ModerationEvent
from django.utils.timezone import now


class ModerationEventUpdateSerializer(ModelSerializer):

    contributor_id = IntegerField(source='contributor.id', read_only=True)
    contributor_name = CharField(source='contributor.name', read_only=True)
    source = CharField(read_only=True)
    os_id = CharField(source='os.id', read_only=True)
    claim_id = IntegerField(source='claim.id', read_only=True)

    class Meta:
        model = ModerationEvent
        fields = [
            'uuid',
            'created_at',
            'updated_at',
            'os_id',
            'contributor_id',
            'contributor_name',
            'cleaned_data',
            'request_type',
            'source',
            'status',
            'status_change_date',
            'claim_id'
        ]

    def __init__(
        self,
        instance=None,
        data=empty,
        user=None,
        partial=False,
        **kwargs
    ):
        self.__moderator = user
        super().__init__(
            instance=instance,
            data=data,
            partial=partial,
            **kwargs
        )

    def to_internal_value(self, data):
        status = data.get('status')

        if status is None:
            raise ValidationError({
                "field": "status",
                "detail": "This field is required."
            })

        self.__validate_status(status)
        return super().to_internal_value(data)

    def __validate_status(self, value):
        if value not in [
            ModerationEvent.Status.PENDING,
            ModerationEvent.Status.APPROVED,
            ModerationEvent.Status.REJECTED
        ]:
            raise ValidationError({
                "field": "status",
                "detail": (
                    "Moderation status must be one of "
                    "PENDING, APPROVED or REJECTED."
                )
            })
        return value

    def update(self, instance, validated_data):
        if 'status' in validated_data:
            value = validated_data['status']
            if value == ModerationEvent.Status.REJECTED:
                instance.action_type = ModerationEvent.ActionType.REJECTED
                instance.action_perform_by = self.__moderator

            instance.status = value
            instance.status_change_date = now()

        instance.save()
        return instance

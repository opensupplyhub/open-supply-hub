from rest_framework.serializers import (
    ModelSerializer,
    ValidationError
)
from api.models.moderation_event \
    import ModerationEvent
from django.utils.timezone import now


class ModerationEventUpdateSerializer(ModelSerializer):

    class Meta:
        model = ModerationEvent
        fields = [
            'uuid',
            'created_at',
            'updated_at',
            'status_change_date',
            'contributor',
            'os',
            'claim',
            'request_type',
            'raw_data',
            'cleaned_data',
            'geocode_result',
            'status',
            'source'
        ]

    def to_internal_value(self, data):
        # Ensure custom status validation is triggered.
        status = data.get('status')

        # Check if 'status' is provided, else raise validation error
        if status is None:
            raise ValidationError({
                "field": "status",
                "message": "This field is required."
            })

        # Invoke validate_status to enforce custom validation
        self.validate_status(status)
        return super().to_internal_value(data)

    def validate_status(self, value):
        # Validation for status field.
        if value not in [
            ModerationEvent.Status.PENDING,
            ModerationEvent.Status.RESOLVED
        ]:
            raise ValidationError({
                "field": "status",
                "message": f"'{value}' is not a valid status."
            })
        return value

    def update(self, instance, validated_data):
        # Check if the status field is updated
        if 'status' in validated_data:
            value = validated_data['status']
            # Update status value
            instance.status = value
            # Automatically update status_change_date
            instance.status_change_date = now()

        # Save the instance with the new values
        instance.save()
        return instance

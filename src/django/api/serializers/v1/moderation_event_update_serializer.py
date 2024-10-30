from rest_framework.serializers import (
    ModelSerializer,
    ValidationError,
    CharField,
    IntegerField
)
from api.models.moderation_event \
    import ModerationEvent
from django.utils.timezone import now


class ModerationEventUpdateSerializer(ModelSerializer):

    # Add a custom field and provide naming for response
    contributor_id = IntegerField(source='contributor.id', read_only=True)
    contributor_name = CharField(source='contributor.name', read_only=True)
    os_id = IntegerField(source='os.id', read_only=True)
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

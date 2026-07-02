from rest_framework.serializers import (
    ModelSerializer,
    ValidationError,
    CharField,
    IntegerField,
    SerializerMethodField
)
from rest_framework.fields import empty
from api.models.moderation_event \
    import ModerationEvent
from django.utils.timezone import now


class ModerationEventUpdateSerializer(ModelSerializer):
    MIN_REASON_TEXT_LENGTH = 30

    action_reason_text_cleaned = CharField(write_only=True, required=False)
    action_reason_text_raw = CharField(write_only=True, required=False)

    contributor_id = IntegerField(source='contributor.id', read_only=True)
    contributor_name = CharField(source='contributor.name', read_only=True)
    source = CharField(read_only=True)
    os_id = SerializerMethodField()
    os_id_snapshot = SerializerMethodField()
    claim_id = IntegerField(source='claim.id', read_only=True)

    class Meta:
        model = ModerationEvent
        fields = [
            'uuid',
            'created_at',
            'updated_at',
            'os_id',
            'os_id_snapshot',
            'contributor_id',
            'contributor_name',
            'cleaned_data',
            'request_type',
            'source',
            'status',
            'status_change_date',
            'claim_id',
            'action_reason_text_cleaned',
            'action_reason_text_raw',
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

    def get_os_id(self, obj):
        # Mirror the OpenSearch-backed GET endpoints, which serve
        # COALESCE(NULLIF(os_id_snapshot, ''), os_id): the snapshot (written
        # once at approval) takes precedence, falling back to the live os FK
        # only when the snapshot is unset. Preserves the originally-approved
        # OS ID after a facility delete/merge. See OSDEV-2920 / OSDEV-2696.
        # obj.os_id reads the FK column directly: it is None once the facility
        # is deleted/merged (SET_NULL), and avoids the extra query that os.id
        # would trigger by dereferencing the related object.
        return obj.os_id_snapshot or obj.os_id or None

    def get_os_id_snapshot(self, obj):
        # Expose the snapshot as its own field (null when unset), matching the
        # GET endpoints which surface NULLIF(os_id_snapshot, '').
        # `or None`: os_id_snapshot defaults to '' (falsy), so an unset
        # snapshot serializes as JSON null rather than "", matching GET.
        return obj.os_id_snapshot or None

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

    def validate(self, data):
        status = data.get('status')

        if status != ModerationEvent.Status.REJECTED:
            return data

        cleaned = data.get('action_reason_text_cleaned')
        raw = data.get('action_reason_text_raw')
        errors = []

        if not cleaned:
            errors.append({
                "field": "action_reason_text_cleaned",
                "detail": (
                    "This field is required when rejecting a moderation "
                    "event."
                )
            })
        elif len(cleaned) < self.MIN_REASON_TEXT_LENGTH:
            errors.append({
                "field": "action_reason_text_cleaned",
                "detail": "This field must be at least 30 characters."
            })

        if not raw:
            errors.append({
                "field": "action_reason_text_raw",
                "detail": (
                    "This field is required when rejecting a moderation "
                    "event."
                )
            })
        elif len(raw) < self.MIN_REASON_TEXT_LENGTH:
            errors.append({
                "field": "action_reason_text_raw",
                "detail": "This field must be at least 30 characters."
            })

        if errors:
            raise ValidationError(errors)

        return data

    def update(self, instance, validated_data):
        if 'status' in validated_data:
            value = validated_data['status']
            if value == ModerationEvent.Status.REJECTED:
                instance.action_type = ModerationEvent.ActionType.REJECTED
                instance.action_perform_by = self.__moderator
                instance.action_reason_text_cleaned = validated_data[
                    'action_reason_text_cleaned'
                ]
                instance.action_reason_text_raw = validated_data[
                    'action_reason_text_raw'
                ]

            instance.status = value
            instance.status_change_date = now()

        instance.save()
        return instance

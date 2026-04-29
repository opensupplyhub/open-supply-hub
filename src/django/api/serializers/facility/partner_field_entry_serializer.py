from rest_framework import serializers


class PartnerFieldEntrySerializer(serializers.Serializer):
    """Schema for a single partner field entry as produced by
    FacilityIndexExtendedFieldListSerializer."""

    id = serializers.IntegerField(read_only=True)
    is_verified = serializers.BooleanField(read_only=True)
    value = serializers.JSONField(read_only=True, allow_null=True)
    created_at = serializers.DateTimeField(read_only=True, required=False)
    updated_at = serializers.DateTimeField(read_only=True)
    contributor_name = serializers.CharField(read_only=True, allow_null=True)
    contributor_id = serializers.IntegerField(read_only=True, allow_null=True)
    value_count = serializers.IntegerField(read_only=True)
    verified_count = serializers.IntegerField(read_only=True)
    is_from_claim = serializers.BooleanField(read_only=True)
    field_name = serializers.CharField(read_only=True)
    source_by = serializers.CharField(
        read_only=True, allow_null=True, allow_blank=True
    )
    unit = serializers.CharField(read_only=True, allow_blank=True)
    label = serializers.CharField(read_only=True, allow_blank=True)
    base_url = serializers.CharField(read_only=True, allow_blank=True)
    display_text = serializers.CharField(read_only=True, allow_blank=True)
    json_schema = serializers.JSONField(read_only=True, allow_null=True)

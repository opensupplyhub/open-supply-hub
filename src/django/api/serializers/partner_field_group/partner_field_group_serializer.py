"""
Serializer for partner field groups.
Specifies the fields that are returned by
the GET /api/partner-field-groups/ API endpoint.
"""

from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from api.models.partner_field_group import PartnerFieldGroup


class PartnerFieldSerializer(serializers.Serializer):
    """
    Nested serializer for individual partner fields within a group.
    Exposes the name (query-string key) and display label.
    """

    name = serializers.CharField()
    label = serializers.CharField()


class PartnerFieldGroupSerializer(ModelSerializer):
    """
    Serializer for the PartnerFieldGroup model.
    Serializes the fields and related partner_fields for the API response.
    """

    partner_fields = PartnerFieldSerializer(many=True, read_only=True)

    class Meta:
        """
        Meta class for partner field group serializer.
        Specifies the fields that are returned by the API response.
        """

        model = PartnerFieldGroup
        fields = [
            "uuid",
            "name",
            "order",
            "icon_file",
            "description",
            "helper_text",
            "partner_fields",
            "created_at",
            "updated_at",
        ]

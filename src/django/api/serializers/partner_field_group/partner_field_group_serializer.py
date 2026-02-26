"""
Serializer for partner field groups.
"""

from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from api.models.partner_field_group import PartnerFieldGroup


class PartnerFieldGroupSerializer(ModelSerializer):
    """
    Serializer for partner field groups.
    """

    partner_fields = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="name",
    )

    class Meta:
        """
        Meta class for partner field group serializer.
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

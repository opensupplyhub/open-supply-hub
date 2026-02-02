"""
Serializer for partner fields.
"""

from rest_framework.serializers import ModelSerializer
from api.models.partner_field import PartnerField


class PartnerFieldSerializer(ModelSerializer):
    """
    Serializer for partner fields.
    """

    class Meta:
        """
        Meta class for partner field serializer.
        """

        model = PartnerField
        fields = [
            "uuid",
            "name",
            "type",
            "json_schema",
            "active",
            "system_field",
            "created_at",
            "updated_at",
        ]

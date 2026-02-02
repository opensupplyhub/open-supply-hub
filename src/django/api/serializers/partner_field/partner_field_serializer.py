from rest_framework.serializers import ModelSerializer
from api.models.partner_field import PartnerField


class PartnerFieldSerializer(ModelSerializer):
    class Meta:
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

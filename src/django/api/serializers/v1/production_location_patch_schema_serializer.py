from rest_framework import serializers
from api.serializers.v1.production_location_schema_serializer \
    import ProductionLocationSchemaSerializer


class ProductionLocationPatchSchemaSerializer(
    ProductionLocationSchemaSerializer
):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._set_core_required(False)

    def validate(self, data):
        if not data:
            raise serializers.ValidationError([
                {
                    'field': 'non_field_errors',
                    'detail': 'No fields provided.'
                }
            ])
        return super().validate(data)

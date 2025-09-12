from api.serializers.v1.production_location_schema_serializer \
    import ProductionLocationSchemaSerializer


class ProductionLocationPostSchemaSerializer(
    ProductionLocationSchemaSerializer
):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._set_core_required(True)

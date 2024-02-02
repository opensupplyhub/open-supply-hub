from rest_framework.serializers import ModelSerializer
from ..models.embed_field import EmbedField


class EmbedFieldsSerializer(ModelSerializer):
    class Meta:
        model = EmbedField
        fields = ('column_name', 'display_name',
                  'visible', 'order', 'searchable')

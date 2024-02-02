from rest_framework.serializers import (
    ModelSerializer,
    SerializerMethodField,
)
from ..models import (
    Contributor,
    EmbedConfig,
    EmbedField,
    ExtendedField
)
from .embed_fields import EmbedFieldsSerializer


class EmbedConfigSerializer(ModelSerializer):
    contributor = SerializerMethodField()
    embed_fields = SerializerMethodField()
    contributor_name = SerializerMethodField()
    extended_fields = SerializerMethodField()

    class Meta:
        model = EmbedConfig
        fields = ('id', 'width', 'height', 'color', 'font', 'contributor',
                  'embed_fields', 'prefer_contributor_name',
                  'contributor_name', 'text_search_label', 'map_style',
                  'extended_fields', 'hide_sector_data')

    def get_contributor(self, instance):
        try:
            return instance.contributor.id
        except Contributor.DoesNotExist:
            return None

    def get_contributor_name(self, instance):
        try:
            return instance.contributor.name
        except Contributor.DoesNotExist:
            return None

    def get_embed_fields(self, instance):
        embed_fields = (
            EmbedField
            .objects
            .filter(embed_config=instance)
            .order_by('order')
        )
        return EmbedFieldsSerializer(embed_fields, many=True).data

    def get_extended_fields(self, instance):
        try:
            extended_fields = (
                ExtendedField
                .objects
                .filter(contributor_id=instance.contributor.id)
                .values_list('field_name', flat=True).distinct()
            )
            return extended_fields
        except Contributor.DoesNotExist:
            return []

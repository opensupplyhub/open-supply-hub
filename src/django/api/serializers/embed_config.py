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
            contributor_field_names = (
                ExtendedField
                .objects
                .filter(contributor_id=instance.contributor.id)
                .values_list('field_name', flat=True).distinct()
            )
            visible_column_names = set(
                EmbedField
                .objects
                .filter(embed_config=instance, visible=True)
                .values_list('column_name', flat=True)
            )
            return [
                field_name for field_name in contributor_field_names
                if field_name in visible_column_names
            ]
        except Contributor.DoesNotExist:
            return []

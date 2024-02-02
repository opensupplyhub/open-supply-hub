from rest_framework.serializers import (
    ModelSerializer,
    SerializerMethodField,
)
from django.db.models import Q
from ..models.facility.facility_match import FacilityMatch
from ..models.extended_field import ExtendedField
from .utils import (
    get_contributor_id,
    get_contributor_name,
)


class ExtendedFieldListSerializer(ModelSerializer):
    contributor_name = SerializerMethodField()
    contributor_id = SerializerMethodField()
    value_count = SerializerMethodField()
    is_from_claim = SerializerMethodField()
    verified_count = SerializerMethodField()

    class Meta:
        model = ExtendedField
        fields = ('id', 'is_verified', 'value', 'created_at', 'updated_at',
                  'contributor_name', 'contributor_id', 'value_count',
                  'is_from_claim', 'field_name', 'verified_count')

    def __init__(self, *args, **kwargs):
        exclude_fields = kwargs.pop('exclude_fields', None)
        super().__init__(*args, **kwargs)

        if exclude_fields:
            for field_name in exclude_fields:
                self.fields.pop(field_name, None)

    def should_display_contributor(self, instance):
        user_can_see_detail = self.context.get("user_can_see_detail")

        should_display_association = True
        list_item_id = instance.facility_list_item_id
        if list_item_id is not None:
            matches = (
                FacilityMatch
                .objects
                .filter(facility_list_item_id=list_item_id)
            )
            should_display_association = any([
                m.should_display_association for m in matches
            ])

        return should_display_association and user_can_see_detail

    def get_contributor_name(self, instance):
        embed_mode_active = self.context.get("embed_mode_active")
        if embed_mode_active:
            return None
        return get_contributor_name(instance.contributor,
                                    self.should_display_contributor(instance))

    def get_contributor_id(self, instance):
        embed_mode_active = self.context.get("embed_mode_active")
        if embed_mode_active:
            return None
        return get_contributor_id(
            instance.contributor,
            self.should_display_contributor(instance)
        )

    def get_value_count(self, instance):
        from_claim = Q(facility_list_item=None)
        from_active_list = Q(facility_list_item__source__is_active=True)
        vals = (
            ExtendedField
            .objects
            .filter(facility=instance.facility)
            .filter(field_name=instance.field_name)
            .filter(value=instance.value)
            .filter(from_claim | from_active_list)
            .count()
        )
        return vals

    def get_is_from_claim(self, instance):
        return instance.facility_list_item is None

    def get_verified_count(self, instance):
        count = 0
        if instance.contributor.is_verified:
            count += 1
        if instance.is_verified:
            count += 1
        return count

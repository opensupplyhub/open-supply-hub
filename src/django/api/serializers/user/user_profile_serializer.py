from rest_framework.serializers import (
    ModelSerializer,
    SerializerMethodField,
)
from ...models import Contributor, FacilityList, User
from ..embed_config import EmbedConfigSerializer
from ..facility.facility_list_summary_serializer import (
    FacilityListSummarySerializer
)


class UserProfileSerializer(ModelSerializer):
    name = SerializerMethodField()
    description = SerializerMethodField()
    website = SerializerMethodField()
    contributor_type = SerializerMethodField()
    other_contributor_type = SerializerMethodField()
    facility_lists = SerializerMethodField()
    is_verified = SerializerMethodField()
    is_moderation_mode = SerializerMethodField()
    embed_config = SerializerMethodField()
    contributor_id = SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'name', 'description', 'website', 'contributor_type',
                  'other_contributor_type', 'facility_lists', 'is_verified',
                  'is_moderation_mode', 'embed_config', 'contributor_id')
        read_only_fields = ('contributor_id',)

    def get_name(self, user):
        try:
            return user.contributor.name
        except Contributor.DoesNotExist:
            return None

    def get_description(self, user):
        try:
            return user.contributor.description
        except Contributor.DoesNotExist:
            return None

    def get_website(self, user):
        try:
            return user.contributor.website
        except Contributor.DoesNotExist:
            return None

    def get_contributor_type(self, user):
        try:
            return user.contributor.contrib_type
        except Contributor.DoesNotExist:
            return None

    def get_other_contributor_type(self, user):
        try:
            return user.contributor.other_contrib_type
        except Contributor.DoesNotExist:
            return None

    def get_contributor_id(self, user):
        try:
            return user.contributor.id
        except Contributor.DoesNotExist:
            return None

    def get_facility_lists(self, user):
        try:
            contributor = user.contributor
            return FacilityListSummarySerializer(
                FacilityList.objects.filter(
                    source__contributor=contributor,
                    source__is_active=True,
                    source__is_public=True,
                ).order_by('-created_at'),
                many=True,
            ).data
        except Contributor.DoesNotExist:
            return []

    def get_is_verified(self, user):
        try:
            return user.contributor.is_verified
        except Contributor.DoesNotExist:
            return False

    def get_is_moderation_mode(self, user):
        return user.is_moderation_mode

    def get_embed_config(self, user):
        try:
            return EmbedConfigSerializer(user.contributor.embed_config).data
        except Contributor.DoesNotExist:
            return None

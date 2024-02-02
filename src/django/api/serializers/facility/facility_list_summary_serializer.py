from rest_framework.serializers import (
    SerializerMethodField,
    ModelSerializer,
)
from ...models import Contributor, FacilityList


class FacilityListSummarySerializer(ModelSerializer):
    contributor_id = SerializerMethodField()

    class Meta:
        model = FacilityList
        fields = ('id', 'name', 'description', 'contributor_id')

    def get_contributor_id(self, facility_list):
        try:
            return facility_list.source.contributor.id
        except Contributor.DoesNotExist:
            return None

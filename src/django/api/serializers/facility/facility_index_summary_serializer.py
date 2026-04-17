from rest_framework_gis.serializers import GeoFeatureModelSerializer

from ...models.facility.facility_index import FacilityIndex


class FacilityIndexSummarySerializer(GeoFeatureModelSerializer):
    class Meta:
        model = FacilityIndex
        fields = (
            'id',
            'name',
            'address',
            'location',
            'country_code',
            'contributors_id',
        )
        geo_field = 'location'

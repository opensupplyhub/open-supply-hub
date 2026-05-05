from rest_framework_gis.serializers import GeoFeatureModelSerializer

from ...models.facility.facility_index import FacilityIndex


class FacilityIndexSummarySerializer(GeoFeatureModelSerializer):
    """Compact GeoJSON serializer exposing core FacilityIndex fields."""

    class Meta:
        model = FacilityIndex
        fields = (
            "id",
            "name",
            "address",
            "country_code",
            "contributors_id",
        )
        geo_field = "location"

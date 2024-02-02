from rest_framework.serializers import (
    SerializerMethodField,
    ModelSerializer,
)
from ...models import FacilityMatch


class FacilityMatchSerializer(ModelSerializer):
    os_id = SerializerMethodField()
    name = SerializerMethodField()
    address = SerializerMethodField()
    location = SerializerMethodField()

    class Meta:
        model = FacilityMatch
        fields = ('id', 'status', 'confidence', 'results',
                  'os_id', 'name', 'address', 'location',
                  'is_active')

    def get_os_id(self, match):
        return match.facility.id

    def get_name(self, match):
        return match.facility.name

    def get_address(self, match):
        return match.facility.address

    def get_location(self, match):
        [lng, lat] = match.facility.location

        return {"lat": lat, "lng": lng}

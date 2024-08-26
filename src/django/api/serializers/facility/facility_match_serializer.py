from api.constants import FacilityClaimStatuses
from api.models.facility.facility_claim import FacilityClaim
from api.models.facility.facility_match import FacilityMatch
from rest_framework.serializers import (
    SerializerMethodField,
    ModelSerializer,
)


class FacilityMatchSerializer(ModelSerializer):
    os_id = SerializerMethodField()
    name = SerializerMethodField()
    address = SerializerMethodField()
    location = SerializerMethodField()
    is_claimed = SerializerMethodField()

    class Meta:
        model = FacilityMatch
        fields = ('id', 'status', 'confidence', 'results',
                  'os_id', 'name', 'address', 'location',
                  'is_active', 'is_claimed')

    def get_os_id(self, match):
        return match.facility.id

    def get_name(self, match):
        return match.facility.name

    def get_address(self, match):
        return match.facility.address

    def get_location(self, match):
        [lng, lat] = match.facility.location

        return {"lat": lat, "lng": lng}

    def get_is_claimed(self, match):
        return FacilityClaim.objects.filter(
            facility=match.facility,
            status=FacilityClaimStatuses.APPROVED
        ).exists()

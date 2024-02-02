from api.models import FacilityList
from api.serializers import FacilityListSerializer

from django.test import TestCase


class ListWithoutSourceTest(TestCase):
    def test_str(self):
        facility_list = FacilityList()
        # We are checking that the __str__ method does not raise an exception.
        str(facility_list)

    def test_serializer(self):
        facility_list = FacilityList()
        # Checking the `data` property triggers the serialization. We are
        # checking that it does not raise an exception.
        FacilityListSerializer(facility_list).data

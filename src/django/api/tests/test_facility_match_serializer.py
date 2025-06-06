from django.test import TestCase
from django.contrib.gis.geos import Point

from api.constants import FacilityClaimStatuses
from api.models.facility.facility import Facility
from api.models.facility.facility_claim import FacilityClaim
from api.models.facility.facility_list_item import FacilityListItem
from api.models.facility.facility_match import FacilityMatch
from api.models.source import Source
from api.models.user import User
from api.models.contributor.contributor import Contributor
from api.models.facility.facility_list import FacilityList
from api.serializers.facility.facility_match_serializer \
    import FacilityMatchSerializer


class FacilityMatchSerializerTest(TestCase):
    def setUp(self):
        self.user_email = "test@example.com"
        self.user_password = "example123"
        self.user = User.objects.create(email=self.user_email)
        self.user.set_password(self.user_password)
        self.user.save()

        self.contributor = Contributor.objects.create(
            admin=self.user,
            name="test contributor 1",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )

        self.list = FacilityList.objects.create(
            header="header", file_name="one", name="First List"
        )

        self.source = Source.objects.create(
            facility_list=self.list,
            source_type=Source.LIST,
            is_active=True,
            is_public=True,
            contributor=self.contributor,
        )

        self.list_item = FacilityListItem.objects.create(
            name="Item",
            address="Address",
            country_code="US",
            sector=["Apparel"],
            row_index=1,
            geocoded_point=Point(0, 0),
            status=FacilityListItem.CONFIRMED_MATCH,
            source=self.source,
            source_uuid=self.source,
        )

        self.facility = Facility.objects.create(
            name="Name",
            address="Address",
            country_code="US",
            location=Point(0, 0),
            created_from=self.list_item,
        )

        self.facility_match = FacilityMatch.objects.create(
            status=FacilityMatch.AUTOMATIC,
            facility=self.facility,
            facility_list_item=self.list_item,
            confidence=0.85,
            results="",
        )

    def test_facility_match_serializer_fields(self):
        serializer = FacilityMatchSerializer(self.facility_match)
        data = serializer.data

        self.assertEqual(data['os_id'], self.facility.id)

        self.assertEqual(data['name'], self.facility.name)

        self.assertEqual(data['address'], self.facility.address)

        expected_location = {"lat": 0.0, "lng": 0.0}
        self.assertEqual(data['location'], expected_location)

        self.assertFalse(data['is_claimed'])

    def test_is_claimed_field_with_claim(self):
        FacilityClaim.objects.create(
            facility=self.facility,
            contributor=self.contributor,
            status=FacilityClaimStatuses.APPROVED
        )

        serializer = FacilityMatchSerializer(self.facility_match)
        data = serializer.data

        self.assertTrue(data['is_claimed'])

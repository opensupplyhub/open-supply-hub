from api.models import (
    Contributor,
    Facility,
    FacilityClaim,
    FacilityList,
    FacilityListItem,
    Source,
    User,
)
from api.constants import FacilityClaimStatuses
from api.serializers import ApprovedFacilityClaimSerializer
from api.serializers import FacilityClaimSerializer

from django.utils import timezone
from django.contrib.gis.geos import Point
from django.test import TestCase


class FacilityClaimSerializerTest(TestCase):
    def setUp(self):
        self.email = "test@example.com"
        self.password = "password"
        self.name = "Test User"
        self.user = User(email=self.email)
        self.user.set_password(self.password)
        self.user.save()

        self.contributor = Contributor.objects.create(
            name=self.name, admin=self.user
        )

        self.facility_list = FacilityList.objects.create(
            header="header", file_name="one", name="one"
        )

        self.source = Source.objects.create(
            facility_list=self.facility_list,
            source_type=Source.LIST,
            is_active=True,
            is_public=True,
            contributor=self.contributor,
        )

        self.list_item = FacilityListItem.objects.create(
            name="Name",
            address="Address",
            country_code="US",
            sector=["Apparel"],
            raw_header="header",
            raw_json={},
            row_index=1,
            status=FacilityListItem.CONFIRMED_MATCH,
            source=self.source,
        )

        self.facility = Facility.objects.create(
            name=self.list_item.name,
            address=self.list_item.address,
            country_code=self.list_item.country_code,
            location=Point(0, 0),
            created_from=self.list_item,
        )

        self.claim = FacilityClaim.objects.create(
            contributor=self.contributor,
            facility=self.facility,
            status=FacilityClaimStatuses.APPROVED,
        )

    def test_product_and_production_options_are_serialized(self):
        data = ApprovedFacilityClaimSerializer(self.claim).data

        self.assertIn("production_type_choices", data)
        self.assertIsNotNone(data["production_type_choices"])
        self.assertNotEqual([], data["production_type_choices"])

    def test_claim_decision(self):
        claim_one = FacilityClaim.objects.create(
            contributor=self.contributor,
            facility=self.facility,
            status=FacilityClaimStatuses.PENDING,
        )
        data_one = FacilityClaimSerializer(claim_one).data

        self.assertIsNone(data_one["claim_decision"])

        date = timezone.now()

        claim_one.status_change_date = date
        claim_one.save()

        data_two = FacilityClaimSerializer(claim_one).data

        self.assertEqual(data_two["claim_decision"], date)

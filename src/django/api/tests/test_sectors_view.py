from django.contrib.gis.geos import Point
from django.urls import reverse

from rest_framework import status

from api.constants import FacilityClaimStatuses
from api.models.contributor.contributor import Contributor
from api.models.facility.facility import Facility
from api.models.facility.facility_claim import FacilityClaim
from api.models.facility.facility_list import FacilityList
from api.models.facility.facility_list_item import FacilityListItem
from api.models.sector import Sector
from api.models.sector_group import SectorGroup
from api.models.source import Source
from api.models.user import User
from api.tests.facility_api_test_case_base import FacilityAPITestCaseBase


class SectorsViewTest(FacilityAPITestCaseBase):
    def setUp(self):
        super().setUp()

        self.user_email_2 = "test2@example.com"
        self.user_password_2 = "example123"
        self.user_2 = User.objects.create(email=self.user_email_2)
        self.user_2.set_password(self.user_password_2)
        self.user_2.save()

        self.contributor_2 = Contributor.objects.create(
            admin=self.user_2,
            name="test contributor 2",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )

        self.list_2 = FacilityList.objects.create(
            header="header", file_name="two", name="Second List"
        )

        self.source_2 = Source.objects.create(
            facility_list=self.list_2,
            source_type=Source.LIST,
            is_active=True,
            is_public=True,
            contributor=self.contributor_2,
        )

        self.list_item_2 = FacilityListItem.objects.create(
            name="Item 2",
            address="Address 2",
            country_code="US",
            sector=["Health", "Information"],
            row_index=2,
            geocoded_point=Point(0, 0),
            status=FacilityListItem.MATCHED,
            source=self.source_2,
        )

        self.facility_2 = Facility.objects.create(
            name="Name 2",
            address="Address 2",
            country_code="US",
            location=Point(0, 0),
            created_from=self.list_item_2,
        )

        self.claim = FacilityClaim.objects.create(
            contributor=self.contributor_2,
            facility=self.facility,
            sector=["Agriculture", "Health"],
            status=FacilityClaimStatuses.APPROVED,
        )

        self.list_item_2.facility = self.facility_2
        self.list_item_2.save()

        self.sector1 = Sector.objects.create(name="Agriculture")
        self.sector2 = Sector.objects.create(name="Apparel")
        self.sector3 = Sector.objects.create(name="Information")
        self.sector4 = Sector.objects.create(name="Health")
        self.sector5 = Sector.objects.create(name="Manufacturing")

        self.group1 = SectorGroup.objects.create(name="Group 1")
        self.group2 = SectorGroup.objects.create(name="Group 2")

        self.group1.sectors.add(self.sector1, self.sector2)
        self.group2.sectors.add(self.sector3, self.sector4, self.sector5)

        self.url = reverse("sectors")

    def test_get_sectors_without_embed(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            sorted(['Agriculture', 'Apparel', 'Health', 'Information']),
        )
        self.assertNotIn('Manufacturing', response.data)

    def test_get_sectors_with_embed_and_contributor_has_claims(self):
        response = self.client.get(
            self.url, {'embed': 'true', 'contributor': self.contributor_2.id}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data, sorted(['Agriculture', 'Health', 'Information'])
        )

    def test_get_sectors_with_embed_and_contributor_has_no_claims(self):
        response = self.client.get(
            self.url, {'embed': 'true', 'contributor': self.contributor.id}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, ['Apparel'])

    def test_get_sectors_with_embed_without_contributor(self):
        response = self.client.get(self.url, {'embed': 'true'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_get_sectors_with_grouped(self):
        response = self.client.get(self.url, {'grouped': 'true'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            [
                {
                    'group_name': 'Group 1',
                    'sectors': sorted(['Agriculture', 'Apparel']),
                },
                {
                    'group_name': 'Group 2',
                    'sectors': sorted(['Health', 'Information']),
                },
            ],
        )
        self.assertNotIn(
            'Manufacturing',
            [sector for group in response.data for sector in group['sectors']],
        )

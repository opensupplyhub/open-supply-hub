import json
from unittest.mock import Mock, patch

from api.constants import FeatureGroups
from api.models import Contributor, Source, User
from api.models.facility.facility_index import FacilityIndex
from api.tests.test_facility_api_case_base import FacilityAPITestCaseBase
from api.tests.test_data import geocoding_data

from django.contrib import auth
from django.urls import reverse


class SectorChoiceViewTest(FacilityAPITestCaseBase):
    fixtures = ["sectors"]

    @patch("api.geocoding.requests.get")
    def setUp(self, mock_get):
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

        self.client.logout()
        group = auth.models.Group.objects.get(
            name=FeatureGroups.CAN_SUBMIT_FACILITY,
        )
        self.user_2.groups.set([group.id])
        self.user_2.save()
        self.client.login(
            email=self.user_email_2, password=self.user_password_2
        )

        self.SECTOR_A = "Apparel"
        self.SECTOR_B = "Health"

        mock_get.return_value = Mock(ok=True, status_code=200)
        mock_get.return_value.json.return_value = geocoding_data
        self.client.post(
            reverse("facility-list"),
            json.dumps(
                {
                    "country": "US",
                    "name": "Azavea",
                    "address": "990 Spring Garden St., Philadelphia PA 19123",
                    "sector_product_type": [self.SECTOR_A, self.SECTOR_B],
                }
            ),
            content_type="application/json",
        )

        self.sorted_sector_names = [self.SECTOR_A, self.SECTOR_B]

    # TODO: Replace to Dedupe Hub if possible (issue between test database
    #       & Dedupe Hub live database)
    # def test_sector_choices_basic(self):
    #     response = self.client.get(reverse('sectors'))
    #     print(response.data)
    #     self.assertEqual(response.status_code, 200)

    #     # Response should be sorted and deduped
    #     for index, sector_name in enumerate(self.sorted_sector_names):
    #         self.assertEqual(response.json()[index], sector_name)

    def test_sector_choices_unspecified(self):
        fi = FacilityIndex.objects.first()
        fi.sector = ["Apparel", "Health", "Unspecified"]
        fi.save()

        response = self.client.get(reverse("sectors"))
        self.assertEqual(response.status_code, 200)

        # Response should be sorted and deduped
        for index, sector_name in enumerate(self.sorted_sector_names):
            self.assertEqual(response.json()[index], sector_name)

    def test_sector_choices_embed(self):
        response = self.client.get(
            "{}?contributor={}&embed=1".format(
                reverse("sectors"), self.contributor.id
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

    def test_sector_choices_embed_inactive(self):
        Source.objects.filter(contributor=self.contributor).update(
            is_active=False
        )

        response = self.client.get(
            "{}?contributor={}&embed=1".format(
                reverse("sectors"), self.contributor.id
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 0)

    def test_sector_choices_embed_no_contributor(self):
        response = self.client.get("{}?embed=1".format(reverse("sectors")))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 0)

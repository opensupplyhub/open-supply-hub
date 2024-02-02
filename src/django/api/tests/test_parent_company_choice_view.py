from api.models import Contributor, User
from api.models.facility.facility_index import FacilityIndex
from rest_framework.test import APITestCase

from django.contrib.gis.geos import Point
from django.urls import reverse


class ParentCompanyChoiceViewTest(APITestCase):
    def setUp(self):
        super().setUp()
        email = "test@example.com"
        password = "example123"
        self.user = User.objects.create(email=email)
        self.user.set_password(password)
        self.user.save()

        self.client.login(email=email, password=password)

    def test_company_choices_null(self):
        indexes = [
            FacilityIndex(
                name="Name",
                country_code="US",
                location=Point(0, 0),
                sector=[],
                contrib_types=[],
                contributors=[],
                lists=[],
                id=i,
                contributors_count=0,
                contributors_id=[],
                approved_claim_ids=[],
                facility_names=[],
                facility_addresses=[],
                extended_fields=[],
            )
            for i in range(10)
        ]
        FacilityIndex.objects.bulk_create(indexes)
        response = self.client.get(reverse("parent_companies"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])
        self.assertEqual(len(response.json()), 0)

    def test_company_choices_no_values(self):
        indexes = [
            FacilityIndex(
                name="Name",
                country_code="US",
                location=Point(0, 0),
                sector=[],
                contrib_types=[],
                contributors=[],
                lists=[],
                id=i,
                contributors_count=0,
                contributors_id=[],
                approved_claim_ids=[],
                facility_names=[],
                facility_addresses=[],
                extended_fields=[],
            )
            for i in range(10)
        ]
        FacilityIndex.objects.bulk_create(indexes)
        response = self.client.get(reverse("parent_companies"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])
        self.assertEqual(len(response.json()), 0)

    def test_company_choices_basic(self):
        c1 = Contributor.objects.create(
            name="Brand A", admin=User.objects.create(email="a@example.com")
        )
        c2 = Contributor.objects.create(
            name="Contributor 1",
            admin=User.objects.create(email="b@example.com"),
        )
        Contributor.objects.create(
            name="Contributor 2",
            admin=User.objects.create(email="c@example.com"),
        )
        indexes = [
            FacilityIndex(
                name="Name",
                country_code="US",
                location=Point(0, 0),
                sector=[],
                contrib_types=[],
                contributors=[],
                lists=[],
                id=i,
                contributors_count=0,
                contributors_id=[],
                approved_claim_ids=[],
                facility_names=[],
                facility_addresses=[],
                extended_fields=[],
            )
            for i in range(4)
        ]
        indexes[0].parent_company_id = [c1.id]
        indexes[0].parent_company_name = [c1.name]
        indexes[1].parent_company_name = ["Brand A"]
        indexes[2].parent_company_id = [c2.id]
        indexes[2].parent_company_name = [c2.name]
        indexes[3].parent_company_name = ["Contributor 2", "Brand B"]
        FacilityIndex.objects.bulk_create(indexes)
        response = self.client.get(reverse("parent_companies"))
        self.assertEqual(response.status_code, 200)
        # Response should be sorted and deduped, with names that do not match
        # contributors using the name instead of the id
        self.assertEqual(
            response.json(),
            [
                [c1.id, c1.name],
                ["Brand B", "Brand B"],
                [c2.id, c2.name],
                ["Contributor 2", "Contributor 2"],
            ],
        )

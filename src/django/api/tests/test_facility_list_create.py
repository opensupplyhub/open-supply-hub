import json

from api.models import (
    Contributor,
    FacilityList,
    Source,
    User,
)
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse


class FacilityListCreateTest(APITestCase):
    def setUp(self):
        self.email = "test@example.com"
        self.password = "password"
        self.name = "Test User"
        self.user = User(email=self.email)
        self.user.set_password(self.password)
        self.user.save()

        self.client.post(
            "/user-login/",
            {"email": self.email, "password": self.password},
            format="json",
        )

        self.contributor = Contributor(name=self.name, admin=self.user)
        self.contributor.save()
        self.test_csv_rows = [
            "country,name,address,sector,extra_1",
            "US,Somewhere,999 Park St,Apparel",
            "US,Someplace Else,1234 Main St,Apparel",
        ]
        self.test_file = SimpleUploadedFile(
            "facilities.csv",
            b"\n".join([s.encode() for s in self.test_csv_rows]),
            content_type="text/csv",
        )

    def post_header_only_file(self, **kwargs):
        if kwargs is None:
            kwargs = {}
        csv_file = SimpleUploadedFile(
            "facilities.csv",
            b"country,name,address,sector\n",
            content_type="text/csv",
        )
        return self.client.post(
            reverse("facility-list-list"),
            {"file": csv_file, **kwargs},
            format="multipart",
        )

    def test_creates_list_and_source(self):
        previous_list_count = FacilityList.objects.all().count()
        previous_source_count = Source.objects.all().count()
        response = self.client.post(
            reverse("facility-list-list"),
            {"file": self.test_file},
            format="multipart",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            FacilityList.objects.all().count(), previous_list_count + 1
        )
        self.assertEqual(
            Source.objects.all().count(), previous_source_count + 1
        )

    def test_file_required(self):
        response = self.client.post(reverse("facility-list-list"))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content), ["No file specified."])

    def test_file_and_name_specified(self):
        name = "A list of facilities"
        response = self.post_header_only_file(name=name)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_json = json.loads(response.content)
        new_list = FacilityList.objects.get(id=response_json["id"])
        self.assertEqual(new_list.name, name)

    def test_replaces_must_be_numeric(self):
        previous_list_count = FacilityList.objects.all().count()
        response = self.post_header_only_file(replaces="BAD")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            json.loads(response.content), ['"replaces" must be an integer ID.']
        )
        self.assertEqual(
            FacilityList.objects.all().count(), previous_list_count
        )

    def test_replaces_must_be_a_list_id(self):
        previous_list_count = FacilityList.objects.all().count()
        response = self.post_header_only_file(replaces=0)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            json.loads(response.content), ["0 is not a valid FacilityList ID."]
        )
        self.assertEqual(
            FacilityList.objects.all().count(), previous_list_count
        )

    def test_replaces(self):
        previous_list_count = FacilityList.objects.all().count()

        # Upload original
        response = self.post_header_only_file()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_json = json.loads(response.content)
        original_list = FacilityList.objects.get(pk=response_json["id"])

        self.assertTrue(original_list.source.is_active)

        # Upload replacement
        response = self.post_header_only_file(replaces=response_json["id"])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_json = json.loads(response.content)
        new_list = FacilityList.objects.get(pk=response_json["id"])

        self.assertEqual(
            FacilityList.objects.all().count(), previous_list_count + 2
        )
        self.assertEqual(new_list.replaces.id, original_list.id)
        self.assertEqual(new_list.status, FacilityList.PENDING)

        response = self.client.get(
            reverse("facility-list-detail", args=[original_list.id])
        )
        response_json = json.loads(response.content)
        self.assertEqual(response_json["status"], FacilityList.REPLACED)

        original_list.refresh_from_db()

        self.assertTrue(hasattr(original_list, "replaced_by"))

        # The original list source should not be deactivated. It will be
        # deactived after the replacement is processed
        self.assertTrue(original_list.source.is_active)

    def test_cant_replace_twice(self):
        previous_list_count = FacilityList.objects.all().count()

        # Upload original
        response = self.post_header_only_file()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_json = json.loads(response.content)

        # Upload replacement
        response = self.post_header_only_file(replaces=response_json["id"])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Attempt second replacement
        response = self.post_header_only_file(replaces=response_json["id"])
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            json.loads(response.content),
            [
                "FacilityList {} has already been replaced.".format(
                    response_json["id"]
                )
            ],
        )

        self.assertEqual(
            FacilityList.objects.all().count(), previous_list_count + 2
        )

    def test_user_must_be_authenticated(self):
        self.client.post("/user-logout/")
        response = self.client.post(
            reverse("facility-list-list"),
            {"file": self.test_file},
            format="multipart",
        )
        self.assertEqual(response.status_code, 401)

    def test_upload_with_authentication_token_succeeds(self):
        token = Token.objects.create(user=self.user)
        self.client.post("/user-logout/")
        header = {"HTTP_AUTHORIZATION": "Token {0}".format(token)}
        response = self.client.post(
            reverse("facility-list-list"),
            {"file": self.test_file},
            format="multipart",
            **header
        )
        self.assertEqual(response.status_code, 200)

    def test_get_request_for_user_with_no_lists_returns_empty_array(self):
        response = self.client.get(reverse("facility-list-list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])
        self.assertEqual(len(response.json()), 0)

    def test_get_request_for_user_with_test_file_list_returns_items(self):
        self.client.post(
            reverse("facility-list-list"),
            {"file": self.test_file},
            format="multipart",
        )
        response = self.client.get(reverse("facility-list-list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

    def test_get_request_for_unauthenticated_user_returns_401(self):
        self.client.post("/user-logout/")
        response = self.client.get(reverse("facility-list-list"))
        self.assertEqual(response.status_code, 401)

    def test_get_with_authentication_token_returns_items(self):
        token = Token.objects.create(user=self.user)
        self.client.post("/user-logout/")
        header = {"HTTP_AUTHORIZATION": "Token {0}".format(token)}
        self.client.post(
            reverse("facility-list-list"),
            {"file": self.test_file},
            format="multipart",
            **header
        )
        response = self.client.get(reverse("facility-list-list"), **header)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

    def test_upload_by_user_with_no_contributor_returns_402(self):
        Contributor.objects.all().delete()
        token = Token.objects.create(user=self.user)
        self.client.post("/user-logout/")
        header = {"HTTP_AUTHORIZATION": "Token {0}".format(token)}
        response = self.client.post(
            reverse("facility-list-list"),
            {"file": self.test_file},
            format="multipart",
            **header
        )
        self.assertEqual(response.status_code, 402)

    def test_list_request_by_user_with_no_contributor_returns_400(self):
        Contributor.objects.all().delete()
        response = self.client.get(reverse("facility-list-list"))
        self.assertEqual(response.status_code, 400)

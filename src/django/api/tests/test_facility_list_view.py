import csv

from unittest.mock import patch

from api.models import FacilityList, Source
from api.tests.base_facility_list_test import BaseFacilityListTest

from django.core import mail
from django.test import override_settings


class FacilityListViewTest(BaseFacilityListTest):

    def generate_test_file(self):
        try:
            myfile = open('test.csv', 'w')
            wr = csv.writer(myfile)
            wr.writerow(('name', 'address', 'country'))
            wr.writerow(('Test LTD', 'str Test 17 Test', 'Test'))
            wr.writerow(('Test LTD', 'str Test 78 Test', 'Test'))
        finally:
            myfile.close()

        return myfile

    def test_description_field_list_upload(self):
        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )

        myfile = self.generate_test_file()
        file_path = myfile.name
        f = open(file_path, "r")

        response_one = self.client.post("/api/facility-lists/",
                                        {'file': f,
                                         'name': 'Test',
                                         'description': 'Test'})
        self.assertEqual(200, response_one.status_code)

        response_two = self.client.post("/api/facility-lists/",
                                        {'file': f,
                                         'name': 'Test',
                                         'description': 'Test | Test'})
        self.assertEqual(response_two.json()[0],
                         'Description cannot contain the "|" character.')
        self.assertEqual(400, response_two.status_code)

    def test_superuser_can_list_own_lists(self):
        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )
        response = self.client.get("/api/facility-lists/")

        self.assertEqual(200, response.status_code)

        lists = response.json()

        # Ensure we get the one list
        self.assertEqual(1, len(lists))
        # Ensure it is the right one
        self.assertEqual("Super List", lists[0]["name"])

    def test_user_can_view_own_lists(self):
        self.client.login(email=self.user_email, password=self.user_password)

        for fac_list in [self.list, self.inactive_list, self.private_list]:
            response = self.client.get(
                "/api/facility-lists/{}/".format(fac_list.id)
            )
            self.assertEqual(200, response.status_code)
            self.assertEqual(fac_list.name, response.json()["name"])

    def test_user_cannot_view_others_lists(self):
        self.client.login(email=self.user_email, password=self.user_password)

        response = self.client.get(
            "/api/facility-lists/{}/".format(self.superlist.id)
        )

        self.assertEqual(404, response.status_code)

    def test_superuser_can_view_others_lists(self):
        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )

        superuser_lists = [self.superlist]
        user_lists = [self.list, self.inactive_list, self.private_list]

        for fac_list in superuser_lists + user_lists:
            response = self.client.get(
                "/api/facility-lists/{}/".format(fac_list.id)
            )
            self.assertEqual(200, response.status_code)
            self.assertEqual(fac_list.name, response.json()["name"])

    def test_other_users_cannot_approve(self):
        response = self.client.post(
            "/api/facility-lists/{}/approve/".format(self.superlist.id)
        )

        self.assertEqual(401, response.status_code)

        self.client.login(email=self.user_email, password=self.user_password)

        response = self.client.post(
            "/api/facility-lists/{}/approve/".format(self.superlist.id)
        )

        self.assertEqual(403, response.status_code)

    def test_superuser_can_approve(self):
        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )

        response = self.client.post(
            "/api/facility-lists/{}/approve/".format(self.superlist.id)
        )

        self.assertEqual(200, response.status_code)

        facility_list = FacilityList.objects.get(pk=self.superlist.pk)
        self.assertEqual(FacilityList.APPROVED, facility_list.status)

    def test_other_users_cannot_reject(self):
        response = self.client.post(
            "/api/facility-lists/{}/reject/".format(self.superlist.id)
        )

        self.assertEqual(401, response.status_code)

        self.client.login(email=self.user_email, password=self.user_password)

        response = self.client.post(
            "/api/facility-lists/{}/reject/".format(self.superlist.id)
        )

        self.assertEqual(403, response.status_code)

    def test_source_is_set_to_inactive_on_list_reject(self):
        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )

        response = self.client.post(
            "/api/facility-lists/{}/reject/".format(self.superlist.id)
        )

        self.assertEqual(200, response.status_code)

        source = Source.objects.get(pk=self.superlist.source.pk)
        self.assertEqual(False, source.is_active)

    @override_settings(ENVIRONMENT="production")
    @patch("api.aws_batch.submit_jobs")
    def test_approve_submits_batch_job(self, mock_submit_jobs):
        mock_submit_jobs.return_value = [1]

        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )

        self.client.post(
            "/api/facility-lists/{}/approve/".format(self.superlist.id)
        )

    def test_superuser_can_reject(self):
        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )

        response = self.client.post(
            "/api/facility-lists/{}/reject/".format(self.superlist.id)
        )

        self.assertEqual(200, response.status_code)

        facility_list = FacilityList.objects.get(pk=self.superlist.pk)
        self.assertEqual(FacilityList.REJECTED, facility_list.status)

    def test_rejection_sends_email(self):
        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )

        self.client.post(
            "/api/facility-lists/{}/reject/".format(self.superlist.id)
        )

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.superuser_email])

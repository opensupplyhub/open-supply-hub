import json

from api.constants import LogDownloadQueryParams
from api.models import DownloadLog, User
from rest_framework.test import APITestCase

from django.urls import reverse


class LogDownloadTest(APITestCase):
    def setUp(self):
        self.email = "test@example.com"
        self.password = "password"
        self.name = "Test User"
        self.user = User(email=self.email)
        self.user.set_password(self.password)
        self.user.save()

        self.path = reverse("log_download")

    def test_requires_login(self):
        response = self.client.post(self.path)
        self.assertEqual(401, response.status_code)

    def test_requires_arguments(self):
        self.client.login(email=self.email, password=self.password)
        response = self.client.post(self.path)
        self.assertEqual(400, response.status_code)

        content = json.loads(response.content)
        self.assertIn(LogDownloadQueryParams.PATH, content)
        self.assertIn(LogDownloadQueryParams.RECORD_COUNT, content)

    def test_requires_post(self):
        self.client.login(email=self.email, password=self.password)
        url = "{}?{}={}&{}={}".format(
            self.path,
            LogDownloadQueryParams.PATH,
            "/a/path/",
            LogDownloadQueryParams.RECORD_COUNT,
            1,
        )
        response = self.client.get(url)
        self.assertEqual(405, response.status_code)

    def test_creates_record(self):
        DownloadLog.objects.all().delete()
        self.client.login(email=self.email, password=self.password)
        expected_path = "/a/path"
        expected_record_count = 42
        url = "{}?{}={}&{}={}".format(
            self.path,
            LogDownloadQueryParams.PATH,
            expected_path,
            LogDownloadQueryParams.RECORD_COUNT,
            expected_record_count,
        )
        response = self.client.post(url)
        self.assertEqual(204, response.status_code)

        self.assertEqual(1, DownloadLog.objects.all().count())
        log = DownloadLog.objects.first()
        self.assertEqual(expected_path, log.path)
        self.assertEqual(expected_record_count, log.record_count)

    def test_path_max_length(self):
        DownloadLog.objects.all().delete()
        self.client.login(email=self.email, password=self.password)
        max_length = DownloadLog._meta.get_field('path').max_length
        expected_record_count = 42
        # Create a path exactly at max length.
        path = "a" * max_length
        url = "{}?{}={}&{}={}".format(
            self.path,
            LogDownloadQueryParams.PATH,
            path,
            LogDownloadQueryParams.RECORD_COUNT,
            expected_record_count,
        )
        response = self.client.post(url)
        self.assertEqual(204, response.status_code)

        # Test that path exceeding max_length raises error on full_clean.
        expected_error = "Path length must not exceed 4096 characters."
        too_long_path = "a" * (max_length + 1)
        url = "{}?{}={}&{}={}".format(
            self.path,
            LogDownloadQueryParams.PATH,
            too_long_path,
            LogDownloadQueryParams.RECORD_COUNT,
            expected_record_count,
        )
        response = self.client.post(url)
        self.assertEqual(response.status_code, 400)
        self.assertIn('path', response.data)
        self.assertEqual(response.data['path'][0], expected_error)

from api.helpers import parse_download_date
from rest_framework.test import APITestCase


class CSVDownloadTest(APITestCase):
    def test_parse_download_date(self):
        self.assertEqual(
            "2022-05-18",
            parse_download_date("2022-05-18T07:45:25+00:00")
        )
        self.assertEqual(
            "2020-02-22",
            parse_download_date("2020-02-22T14:39:26.485995+00:00")
        )

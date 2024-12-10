import json

from api.models import FacilityListItem, NonstandardField
from api.constants import APIErrorMessages
from api.tests.facility_api_test_case_base import FacilityAPITestCaseBase

from django.http import QueryDict
from django.urls import reverse


def is_json(myjson):
    try:
        json.loads(myjson)
    except ValueError:
        return False
    return True


class FacilitySubmitTest(FacilityAPITestCaseBase):
    fixtures = ["sectors"]

    def setUp(self):
        super(FacilitySubmitTest, self).setUp()
        self.url = reverse("facility-list")
        self.valid_facility = {
            "country": "United States",
            "name": "Pants Hut",
            "address": "123 Main St, Anywhereville, PA",
            "sector": "Apparel",
            "extra_1": "Extra data",
        }

    def test_unauthenticated_receives_401(self):
        self.client.logout()
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 401)

    def test_not_in_group_receives_403(self):
        self.client.logout()
        self.client.login(email=self.user_email, password=self.user_password)

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 403)

    def test_empty_body_is_invalid(self):
        self.join_group_and_login()
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 400)

    def test_missing_fields_are_invalid(self):
        self.join_group_and_login()

        response = self.client.post(
            self.url,
            {
                "country": "US",
                "name": "Something",
            },
        )
        self.assertEqual(response.status_code, 400)

        response = self.client.post(
            self.url,
            {
                "country": "US",
                "address": "Some street",
            },
        )
        self.assertEqual(response.status_code, 400)

        response = self.client.post(
            self.url,
            {
                "name": "Something",
                "address": "Some street",
            },
        )
        self.assertEqual(response.status_code, 400)

    # TODO: Replace to Dedupe Hub if possible (issue between test database
    #       & Dedupe Hub live database)
    # def test_valid_request(self):
    #     self.join_group_and_login()
    #     response = self.client.post(self.url, self.valid_facility)
    #     self.assertEqual(response.status_code, 201)

    def test_raw_data_with_singlequote(self):
        self.join_group_and_login()
        response = self.client.post(self.url, self.valid_facility)
        data = json.loads(response.content)
        list_item = FacilityListItem.objects.get(id=data["item_id"])
        self.assertEqual(
            list_item.raw_data,
            '"United States","Pants Hut","123 Main St, Anywhereville, PA",'
            '"Apparel","Extra data"',
        )

    def test_raw_data_with_doublequote(self):
        self.join_group_and_login()
        response = self.client.post(
            self.url,
            {
                "country": "United States",
                "name": "Pants Hut",
                "address": "123 Main St, Anywhereville, PA",
                "sector": "Apparel",
                "extra_1": "Extra data",
            },
        )
        data = json.loads(response.content)
        list_item = FacilityListItem.objects.get(id=data["item_id"])
        self.assertEqual(
            list_item.raw_data,
            '"United States","Pants Hut","123 Main St, Anywhereville, PA",'
            '"Apparel","Extra data"',
        )

    def test_raw_data_with_querydict(self):
        self.join_group_and_login()
        query_dict = QueryDict("", mutable=True)
        query_dict.update(self.valid_facility)
        response = self.client.post(self.url, query_dict)
        data = json.loads(response.content)
        list_item = FacilityListItem.objects.get(id=data["item_id"])
        self.assertEqual(
            list_item.raw_data,
            '"United States","Pants Hut","123 Main St, Anywhereville, PA",'
            '"Apparel","Extra data"',
        )

    def test_raw_data_with_internal_quotes(self):
        self.join_group_and_login()
        response = self.client.post(
            self.url,
            {
                "country": "US",
                "name": "Item",
                "address": "Address",
                "extra_2": "d'ataé",
            },
        )
        data = json.loads(response.content)
        list_item = FacilityListItem.objects.get(id=data["item_id"])
        self.assertEqual(list_item.raw_data, '"US","Item","Address","d\'ataé"')

    # TODO: Replace to Dedupe Hub if possible (issue between test database
    #       & Dedupe Hub live database)
    # def test_valid_request_with_params(self):
    #     self.join_group_and_login()
    #     url_with_query = '{}?create=false&public=true'.format(self.url)
    #     response = self.client.post(url_with_query, self.valid_facility)
    #     self.assertEqual(response.status_code, 200)

    # TODO: Replace to Dedupe Hub if possible (issue between test database
    #       & Dedupe Hub live database)
    # def test_private_permission(self):
    #     self.join_group_and_login()
    #     url_with_query = '{}?public=false'.format(self.url)
    #     response = self.client.post(url_with_query, self.valid_facility)
    #     self.assertEqual(response.status_code, 403)

    #     group = auth.models.Group.objects.get(
    #         name=FeatureGroups.CAN_SUBMIT_PRIVATE_FACILITY,
    #     )
    #     self.user.groups.add(group.id)
    #     self.user.save()

    #     response = self.client.post(url_with_query, self.valid_facility)
    #     self.assertEqual(response.status_code, 201)

    def test_creates_nonstandard_fields(self):
        self.join_group_and_login()
        self.client.post(self.url, self.valid_facility)
        fields = NonstandardField.objects.filter(
            contributor=self.user.contributor
        ).values_list("column_name", flat=True)
        self.assertEqual(1, len(fields))
        self.assertIn("extra_1", fields)

    def test_exact_matches_with_create_false(self):
        self.join_group_and_login()
        url_with_query = "{}?create=false&public=true".format(self.url)
        response = self.client.post(url_with_query, self.valid_facility)
        self.assertEqual(response.status_code, 200)
        response_two = self.client.post(url_with_query, self.valid_facility)
        self.assertEqual(response_two.status_code, 200)

    def test_handles_exact_matches_with_empty_strings(self):
        self.join_group_and_login()
        url_with_query = "{}?public=true".format(self.url)
        response = self.client.post(
            url_with_query,
            {
                "country": "United States",
                "name": ",",
                "address": "123 Main St, Anywhereville, PA",
                "extra_1": "Extra data",
            },
        )
        self.assertEqual(response.status_code, 400)
        response_two = self.client.post(
            url_with_query,
            {
                "country": "United States",
                "name": "Pants Hut",
                "address": ",,",
                "extra_1": "Extra data",
            },
        )
        self.assertEqual(response_two.status_code, 400)

    def test_geocoding_no_results(self):
        self.join_group_and_login()
        url_with_query = "{}?public=true".format(self.url)
        response = self.client.post(
            url_with_query,
            {
                "country": 'CN',
                "name": ('Tongxiang Oriental Silk '
                         'Printing and Dyeing Co., Ltd.'),
                "address": ('No.98, Nanshengbang, Dongbangtou Village, '
                            'HeshanTown, '
                            'Tongxiang city., 314599 JIAXING, '
                            'Zhejiang Sheng')
            },
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)
        self.assertEqual(data["status"], FacilityListItem.GEOCODED_NO_RESULTS)
        self.assertEqual(data["message"], APIErrorMessages.GEOCODED_NO_RESULTS)

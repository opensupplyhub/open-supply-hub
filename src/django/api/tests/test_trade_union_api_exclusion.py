from django.http import QueryDict
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from api.models.contributor.contributor import Contributor
from api.models.facility.facility_index import FacilityIndex
from api.models.user import User

# High, fixed id that cannot collide with the small contributor ids referenced
# by the `facilities_index` fixture.
UNION_CONTRIBUTOR_ID = 900001
UNION_FACILITY_ID = '1'

# Web-client (browser) signals: the client key the FE ships and a Referer
# within ALLOWED_HOSTS ('.opensupplyhub.org').
WEB_CLIENT_KEY = 'test-web-client-key'
ALLOWED_REFERER = 'https://os-hub.opensupplyhub.org/facilities'


class TradeUnionApiExclusionBase(APITestCase):
    fixtures = ["facilities_index"]

    def setUp(self):
        union_admin = User.objects.create(email='union-admin@example.com')
        self.union = Contributor.objects.create(
            id=UNION_CONTRIBUTOR_ID,
            admin=union_admin,
            name='Trade Union Contributor',
            contrib_type=Contributor.UNION_CONTRIB_TYPE,
        )
        self.union_facility = FacilityIndex.objects.get(pk=UNION_FACILITY_ID)
        self.union_facility.contributors_id = [self.union.id]
        self.union_facility.save()


class TradeUnionExclusionManagerTest(TradeUnionApiExclusionBase):
    def setUp(self):
        super().setUp()
        self.params = QueryDict('', mutable=True)

    def filtered_ids(self, exclude_trade_union):
        queryset = FacilityIndex.objects.filter_by_query_params(
            self.params, exclude_trade_union=exclude_trade_union
        )
        return set(queryset.values_list('id', flat=True))

    def test_union_facility_excluded_when_flag_on(self):
        self.assertNotIn(self.union_facility.id,
                         self.filtered_ids(exclude_trade_union=True))

    def test_union_facility_included_when_flag_off(self):
        self.assertIn(self.union_facility.id,
                      self.filtered_ids(exclude_trade_union=False))

    def test_non_union_contributor_not_excluded(self):
        self.union.contrib_type = 'Brand / Retailer'
        self.union.save()
        self.assertIn(self.union_facility.id,
                      self.filtered_ids(exclude_trade_union=True))

    def test_filter_trade_union_linked_returns_only_union(self):
        queryset = FacilityIndex.objects.filter_by_query_params(self.params)
        union_ids = set(
            FacilityIndex.objects
            .filter_trade_union_linked(queryset)
            .values_list('id', flat=True)
        )
        self.assertEqual(union_ids, {self.union_facility.id})


class TradeUnionExclusionListViewTest(TradeUnionApiExclusionBase):
    def setUp(self):
        super().setUp()
        self.list_url = reverse('facility-list')

        # API (programmatic) user: authenticates with a token and must have an
        # associated contributor to pass the request-meter middleware.
        self.api_user = User.objects.create(email='api@example.com')
        Contributor.objects.create(
            admin=self.api_user,
            name='API Contributor',
            contrib_type='Brand / Retailer',
        )
        self.token = Token.objects.create(user=self.api_user)

    def feature_ids(self, response):
        return {str(f['id']) for f in response.data['features']}

    def use_token(self):
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {self.token.key}'
        )

    def get_union_scoped_list(self, **extra):
        return self.client.get(
            self.list_url, {'contributors': UNION_CONTRIBUTOR_ID}, **extra
        )

    @override_settings(DEBUG=False, OAR_CLIENT_KEY=WEB_CLIENT_KEY)
    def test_token_request_excludes_union(self):
        self.use_token()
        response = self.get_union_scoped_list()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn(str(self.union_facility.id),
                         self.feature_ids(response))

    @override_settings(DEBUG=False, OAR_CLIENT_KEY=WEB_CLIENT_KEY)
    def test_web_client_request_includes_union(self):
        response = self.get_union_scoped_list(
            HTTP_X_OAR_CLIENT_KEY=WEB_CLIENT_KEY,
            HTTP_REFERER=ALLOWED_REFERER,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(str(self.union_facility.id),
                      self.feature_ids(response))

    @override_settings(DEBUG=False, OAR_CLIENT_KEY=WEB_CLIENT_KEY)
    def test_authenticated_session_without_web_headers_excludes_union(self):
        self.client.force_login(self.api_user)
        response = self.get_union_scoped_list()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn(str(self.union_facility.id),
                         self.feature_ids(response))

    @override_settings(DEBUG=True, OAR_CLIENT_KEY='')
    def test_local_env_includes_union_for_tokenless_request(self):
        # In the local environment client-key checks are bypassed and
        # tokenless traffic is treated as web client, so union data stays
        # visible.
        response = self.get_union_scoped_list()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(str(self.union_facility.id),
                      self.feature_ids(response))

    @override_settings(DEBUG=True, OAR_CLIENT_KEY=WEB_CLIENT_KEY)
    def test_local_env_still_excludes_union_for_token_request(self):
        # Even in the local environment, and even when the request carries
        # genuine web-client headers (which the local bypass would otherwise
        # treat as browser traffic), an API token marks the request as
        # programmatic, so union data is still excluded.
        self.use_token()
        response = self.get_union_scoped_list(
            HTTP_X_OAR_CLIENT_KEY=WEB_CLIENT_KEY,
            HTTP_REFERER=ALLOWED_REFERER,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn(str(self.union_facility.id),
                         self.feature_ids(response))

    @override_settings(DEBUG=False, OAR_CLIENT_KEY=WEB_CLIENT_KEY)
    def test_web_client_reports_excluded_from_download_count(self):
        # Union data is visible to the web client but flagged as
        # non-downloadable so the UI can warn the user.
        response = self.get_union_scoped_list(
            HTTP_X_OAR_CLIENT_KEY=WEB_CLIENT_KEY,
            HTTP_REFERER=ALLOWED_REFERER,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['excluded_from_download_count'], 1)

    @override_settings(DEBUG=False, OAR_CLIENT_KEY=WEB_CLIENT_KEY)
    def test_token_request_reports_zero_excluded_from_download(self):
        # Programmatic callers never see union data, so nothing is reported as
        # hidden from download.
        self.use_token()
        response = self.get_union_scoped_list()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['excluded_from_download_count'], 0)


class TradeUnionExclusionDownloadViewTest(TradeUnionApiExclusionBase):
    def setUp(self):
        super().setUp()
        self.download_url = reverse('facilities-downloads-list')
        self.user = User.objects.create(email='downloader@example.com')
        self.user.set_password('example123')
        self.user.save()
        self.client.force_login(self.user)

    def download(self, params=None):
        return self.client.get(self.download_url, params or {})

    def row_ids(self, response):
        return {row[0] for row in response.data['results']['rows']}

    def test_download_excludes_union_facility(self):
        response = self.download()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn(str(self.union_facility.id), self.row_ids(response))

    def test_download_union_scoped_search_returns_nothing(self):
        response = self.download({'contributors': UNION_CONTRIBUTOR_ID})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), 0)
        self.assertEqual(self.row_ids(response), set())

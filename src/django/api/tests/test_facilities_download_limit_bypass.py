from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError
from rest_framework.test import APITestCase
from waffle.testutils import override_switch

from api.constants import FacilitiesDownloadErrorMessages, FeatureGroups
from api.models.contributor.contributor import Contributor
from api.models.facility_download_limit import FacilityDownloadLimit
from api.models.user import User
from api.services.facilities_download_service import (
    FacilitiesDownloadService,
)


SEND_EMAIL_PATH = (
    'api.services.facilities_download_service.'
    'FacilitiesDownloadService.send_email_if_needed'
)
SESSION_ADD_PATH = (
    'django.core.cache.backends.memcached.BaseMemcachedCache.add'
)


class FacilitiesDownloadLimitBypassTest(APITestCase):
    """
    Covers OSDEV-2139: the download limit must be enforced and charged by
    the server, whichever pages a client decides to request.

    The `facilities_index` fixture has 18 facilities. Facilities are linked
    to contributor ids 1 (3 facilities), 2 (3) and 3 (2).
    """
    fixtures = ['facilities_index']
    total_count = 18

    def setUp(self):
        self.download_url = reverse('facilities-downloads-list')
        self.password = 'example123'
        self.user = self.create_user('downloader@example.com')
        self.limit = FacilityDownloadLimit.objects.create(
            user=self.user,
            free_download_records=5000,
            paid_download_records=0,
        )
        self.client.login(email=self.user.email, password=self.password)

        email_patcher = patch(SEND_EMAIL_PATH, return_value=None)
        self.mock_send_email = email_patcher.start()
        self.addCleanup(email_patcher.stop)

    def create_user(self, email):
        user = User.objects.create(email=email)
        user.set_password(self.password)
        user.save()
        return user

    def create_contributor(self, contributor_id, embed_level=None):
        admin = self.create_user(f'admin{contributor_id}@example.com')
        return Contributor.objects.create(
            id=contributor_id,
            admin=admin,
            name=f'Contributor {contributor_id}',
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
            embed_level=embed_level,
        )

    def get(self, params=None):
        return self.client.get(self.download_url, params or {})

    def download_id_from(self, link):
        return parse_qs(urlsplit(link).query)['download_id'][0]

    def assert_error(self, response, status_code, message):
        self.assertEqual(response.status_code, status_code)
        self.assertIn(message, str(response.data))

    def remaining_records(self):
        self.limit.refresh_from_db()
        return (
            self.limit.free_download_records
            + self.limit.paid_download_records
        )

    # Download sessions

    def test_page_after_first_without_download_id_is_rejected(self):
        response = self.get({'pageSize': 5, 'page': 2})

        self.assert_error(
            response,
            status.HTTP_400_BAD_REQUEST,
            FacilitiesDownloadErrorMessages.SESSION_REQUIRED,
        )
        self.assertEqual(self.remaining_records(), 5000)

    def test_first_page_charges_full_result_set(self):
        response = self.get({'pageSize': 5})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], self.total_count)
        self.assertEqual(len(response.data['results']['rows']), 5)
        self.assertEqual(self.remaining_records(), 5000 - self.total_count)
        self.mock_send_email.assert_called_once()

    def test_following_all_pages_charges_only_once(self):
        response = self.get({'pageSize': 5})
        rows = list(response.data['results']['rows'])

        while response.data['next']:
            response = self.client.get(response.data['next'])
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            rows.extend(response.data['results']['rows'])

        self.assertEqual(len(rows), self.total_count)
        self.assertEqual(len({row[0] for row in rows}), self.total_count)
        self.assertEqual(self.remaining_records(), 5000 - self.total_count)

    def test_skipping_last_page_still_charges(self):
        response = self.get({'pageSize': 5})
        # Stop before the last page, as an aborted download would.
        self.client.get(response.data['next'])

        self.assertEqual(self.remaining_records(), 5000 - self.total_count)

    def test_links_carry_the_same_download_id(self):
        page_1 = self.get({'pageSize': 5})
        page_2 = self.client.get(page_1.data['next'])

        download_id = self.download_id_from(page_1.data['next'])
        self.assertEqual(
            self.download_id_from(page_2.data['next']),
            download_id,
        )
        self.assertEqual(
            self.download_id_from(page_2.data['previous']),
            download_id,
        )

    def test_replaying_first_page_with_download_id_does_not_charge(self):
        page_1 = self.get({'pageSize': 5})
        download_id = self.download_id_from(page_1.data['next'])

        replay = self.get(
            {'pageSize': 5, 'page': 1, 'download_id': download_id}
        )

        self.assertEqual(replay.status_code, status.HTTP_200_OK)
        self.assertEqual(replay.data['count'], self.total_count)
        self.assertEqual(self.remaining_records(), 5000 - self.total_count)

    def test_download_id_with_different_filters_is_rejected(self):
        page_1 = self.get({'pageSize': 2, 'countries': ['US']})
        download_id = self.download_id_from(page_1.data['next'])

        response = self.get({
            'pageSize': 2,
            'page': 2,
            'download_id': download_id,
        })

        self.assert_error(
            response,
            status.HTTP_400_BAD_REQUEST,
            FacilitiesDownloadErrorMessages.SESSION_INVALID,
        )

    def test_download_id_with_different_page_size_is_rejected(self):
        page_1 = self.get({'pageSize': 5})
        download_id = self.download_id_from(page_1.data['next'])

        response = self.get({
            'pageSize': 250,
            'page': 2,
            'download_id': download_id,
        })

        self.assert_error(
            response,
            status.HTTP_400_BAD_REQUEST,
            FacilitiesDownloadErrorMessages.SESSION_INVALID,
        )

    def test_download_id_of_another_user_is_rejected(self):
        page_1 = self.get({'pageSize': 5})
        next_link = page_1.data['next']

        other_user = self.create_user('other@example.com')
        self.client.logout()
        self.client.login(email=other_user.email, password=self.password)

        response = self.client.get(next_link)

        self.assert_error(
            response,
            status.HTTP_400_BAD_REQUEST,
            FacilitiesDownloadErrorMessages.SESSION_INVALID,
        )

    def test_unknown_or_malformed_download_id_is_rejected(self):
        for download_id in ['0' * 32, 'not-a-uuid']:
            response = self.get({
                'pageSize': 5,
                'page': 2,
                'download_id': download_id,
            })
            self.assert_error(
                response,
                status.HTTP_400_BAD_REQUEST,
                FacilitiesDownloadErrorMessages.SESSION_INVALID,
            )

    def test_pages_never_exceed_the_charged_count(self):
        page_1 = self.get({'pageSize': 5})
        download_id = self.download_id_from(page_1.data['next'])

        # Simulate facilities added after the download was charged by
        # lowering the count the session was opened for.
        cache = FacilitiesDownloadService._session_cache()
        key = FacilitiesDownloadService._session_key(download_id)
        session = cache.get(key)
        session['count'] = 7
        cache.set(key, session)

        page_2 = self.client.get(page_1.data['next'])

        self.assertEqual(len(page_2.data['results']['rows']), 2)
        self.assertIsNone(page_2.data['next'])

    def test_limit_is_still_enforced_on_first_page(self):
        self.limit.free_download_records = 3
        self.limit.save()

        response = self.get({'pageSize': 5})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.remaining_records(), 3)

    def test_unavailable_session_cache_fails_closed_without_charging(self):
        with patch(SESSION_ADD_PATH, return_value=False):
            response = self.get({'pageSize': 5})

        self.assert_error(
            response,
            status.HTTP_503_SERVICE_UNAVAILABLE,
            FacilitiesDownloadErrorMessages.SESSION_UNAVAILABLE,
        )
        self.assertEqual(self.remaining_records(), 5000)

    def test_charge_rechecks_limit_under_lock(self):
        # A concurrent download spent the balance after this request's
        # early check, so the in-memory limit is stale.
        stale_limit = FacilityDownloadLimit.objects.get(pk=self.limit.pk)
        FacilityDownloadLimit.objects.filter(pk=self.limit.pk).update(
            free_download_records=2
        )

        with self.assertRaises(ValidationError):
            FacilitiesDownloadService.charge_download(stale_limit, 5)

        self.assertEqual(self.remaining_records(), 2)

    def test_failed_charge_deletes_the_session(self):
        with patch.object(
            FacilitiesDownloadService,
            'charge_download',
            side_effect=ValidationError('limit reached'),
        ), patch.object(
            FacilitiesDownloadService,
            'delete_download_session',
        ) as mock_delete:
            response = self.get({'pageSize': 5})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        mock_delete.assert_called_once()

    def test_email_failure_does_not_fail_charged_download(self):
        self.mock_send_email.side_effect = Exception('Stripe is down')

        response = self.get({'pageSize': 5})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.remaining_records(), 5000 - self.total_count)

    # Authentication and exemptions

    def test_anonymous_download_is_rejected(self):
        self.client.logout()

        response = self.get({'pageSize': 5})

        self.assert_error(
            response,
            status.HTTP_401_UNAUTHORIZED,
            FacilitiesDownloadErrorMessages.LOGIN_REQUIRED,
        )

    @override_switch('private_instance', active=True)
    def test_private_instance_is_not_charged(self):
        response = self.get({'pageSize': 5})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.remaining_records(), 5000)

        page_2 = self.client.get(response.data['next'])
        self.assertEqual(page_2.status_code, status.HTTP_200_OK)

    def test_api_token_download_is_not_charged(self):
        group = Group.objects.get(name=FeatureGroups.CAN_SUBMIT_FACILITY)
        self.user.groups.add(group)
        Contributor.objects.create(
            admin=self.user,
            name='API Contributor',
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )
        token = Token.objects.create(user=self.user)
        self.client.logout()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')

        response = self.get({'pageSize': 5})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.remaining_records(), 5000)

    # Embed mode

    def test_embed_without_contributor_is_rejected(self):
        response = self.get({'embed': 1, 'pageSize': 5})

        self.assert_error(
            response,
            status.HTTP_400_BAD_REQUEST,
            FacilitiesDownloadErrorMessages.EMBED_SINGLE_CONTRIBUTOR,
        )
        self.assertEqual(self.remaining_records(), 5000)

    def test_embed_with_multiple_contributors_is_rejected(self):
        self.create_contributor(1, embed_level=1)
        self.create_contributor(2, embed_level=1)

        response = self.get({'embed': 1, 'contributors': [1, 2]})

        self.assert_error(
            response,
            status.HTTP_400_BAD_REQUEST,
            FacilitiesDownloadErrorMessages.EMBED_SINGLE_CONTRIBUTOR,
        )

    def test_embed_with_mismatched_singular_contributor_is_rejected(self):
        self.create_contributor(1, embed_level=1)

        response = self.get(
            {'embed': 1, 'contributors': 1, 'contributor': 2}
        )

        self.assert_error(
            response,
            status.HTTP_400_BAD_REQUEST,
            FacilitiesDownloadErrorMessages.EMBED_SINGLE_CONTRIBUTOR,
        )

    def test_embed_for_contributor_without_embed_is_rejected(self):
        self.create_contributor(2, embed_level=None)

        for contributor_id in [2, 999]:
            response = self.get({'embed': 1, 'contributors': contributor_id})
            self.assert_error(
                response,
                status.HTTP_400_BAD_REQUEST,
                FacilitiesDownloadErrorMessages.EMBED_NOT_ENABLED,
            )

    def test_valid_embed_is_free_and_limited_to_contributor(self):
        self.create_contributor(2, embed_level=1)
        self.client.logout()

        response = self.get({'embed': 1, 'contributors': 2})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)
        self.assertEqual(len(response.data['results']['rows']), 3)
        self.assertEqual(self.remaining_records(), 5000)

    def test_valid_embed_pages_require_session(self):
        self.create_contributor(2, embed_level=1)
        self.client.logout()

        page_1 = self.get({'embed': 1, 'contributors': 2, 'pageSize': 2})
        page_2 = self.client.get(page_1.data['next'])
        direct_page_2 = self.get(
            {'embed': 1, 'contributors': 2, 'pageSize': 2, 'page': 2}
        )

        self.assertEqual(page_2.status_code, status.HTTP_200_OK)
        self.assertEqual(len(page_2.data['results']['rows']), 1)
        self.assertEqual(
            direct_page_2.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    # Pagination params

    def test_page_size_is_clamped_to_max(self):
        response = self.get({'pageSize': 100000})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['pageSize'], 250)

    def test_invalid_page_params_are_rejected(self):
        cases = [
            ({'page': 0}, FacilitiesDownloadErrorMessages.INVALID_PAGE),
            ({'page': 'abc'}, FacilitiesDownloadErrorMessages.INVALID_PAGE),
            (
                {'pageSize': 'abc'},
                FacilitiesDownloadErrorMessages.INVALID_PAGE_SIZE,
            ),
        ]
        for params, message in cases:
            response = self.get(params)
            self.assert_error(
                response,
                status.HTTP_400_BAD_REQUEST,
                message,
            )
        self.assertEqual(self.remaining_records(), 5000)

import json

from unittest.mock import Mock, patch
from rest_framework.test import APITestCase
from django.urls import reverse
from allauth.account.models import EmailAddress
from waffle.testutils import override_switch

from api.models.moderation_event import ModerationEvent
from api.models.contributor.contributor import Contributor
from api.models.user import User
from api.views.v1.url_names import URLNames
from api.tests.test_data import geocoding_data


class TestProductionLocationsCreate(APITestCase):
    def setUp(self):
        self.url = reverse(URLNames.PRODUCTION_LOCATIONS + '-list')
        self.common_valid_req_body = json.dumps({
            'name': 'Blue Horizon Facility',
            'address': '990 Spring Garden St., Philadelphia PA 19123',
            'country': 'US'
        })

        user_email = 'test@example.com'
        user_password = 'example123'
        self.user = User.objects.create(email=user_email)
        self.user.set_password(user_password)
        self.user.save()

        EmailAddress.objects.create(
            user=self.user, email=user_email, verified=True, primary=True
        )

        Contributor.objects.create(
            admin=self.user,
            name='test contributor 1',
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )

        self.login(user_email, user_password)

    def login(self, email: str, password: str) -> None:
        self.client.logout()
        self.client.login(email=email, password=password)

    def test_only_registered_and_confirmed_has_access(self):
        expected_response_body = {
            'detail': (
                'User must be registered and have confirmed their email to '
                'access.'
            )
        }

        saved_email_address = EmailAddress.objects.get_primary(self.user)
        # Purposely make the email address unverified to trigger a permission
        # error.
        saved_email_address.verified = False
        saved_email_address.save()

        response = self.client.post(self.url,
                                    self.common_valid_req_body,
                                    content_type='application/json')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            json.loads(response.content),
            expected_response_body
        )

    @patch('api.geocoding.requests.get')
    def test_default_throttling_is_applied(self, mock_get):
        mock_get.return_value = Mock(ok=True, status_code=200)
        mock_get.return_value.json.return_value = geocoding_data

        # Simulate 30 requests.
        for _ in range(30):
            response = self.client.post(
                self.url,
                self.common_valid_req_body,
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 202)

            response_body_dict = json.loads(response.content)
            response_moderation_id = response_body_dict.get('moderation_id')
            moderation_event = ModerationEvent.objects.get(
                pk=response_moderation_id
            )
            stringified_created_at = moderation_event.created_at.strftime(
                '%Y-%m-%dT%H:%M:%S.%f'
            ) + 'Z'

            self.assertEqual(
                response_body_dict.get('moderation_status'),
                'PENDING'
            )
            self.assertEqual(
                response_body_dict.get('created_at'),
                stringified_created_at
            )
            self.assertIn("cleaned_data", response_body_dict)
            self.assertEqual(len(response_body_dict), 4)

        # Now simulate the 31st request, which should be throttled.
        throttled_response = self.client.post(
            self.url,
            self.common_valid_req_body,
            content_type='application/json'
        )
        throttled_response_body_dict = json.loads(throttled_response.content)
        self.assertEqual(throttled_response.status_code, 429)
        self.assertEqual(len(throttled_response_body_dict), 1)

    @override_switch('disable_list_uploading', active=True)
    def test_client_cannot_post_when_upload_is_blocked(self):
        expected_error = (
            'Open Supply Hub is undergoing maintenance and not accepting new '
            'data at the moment. Please try again in a few minutes.'
        )

        response = self.client.post(
            self.url,
            self.common_valid_req_body,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 503)

        response_body_dict = json.loads(response.content)
        error = response_body_dict.get('detail')
        self.assertEqual(error, expected_error)
        self.assertEqual(len(response_body_dict), 1)

    def test_endpoint_supports_only_dictionary_structure(self):
        expected_general_error = (
            'The request body is invalid.'
        )
        expected_specific_error = (
            'Invalid data. Expected a dictionary (object), but got list.'
        )
        expected_error_field = 'non_field_errors'

        response = self.client.post(
            self.url,
            [1, 2, 3],
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

        response_body_dict = json.loads(response.content)
        self.assertEqual(len(response_body_dict), 2)

        general_error = response_body_dict['detail']
        errors_list_length = len(response_body_dict['errors'])
        specific_error = response_body_dict['errors'][0]['detail']
        error_field = response_body_dict['errors'][0]['field']
        self.assertEqual(general_error, expected_general_error)
        self.assertEqual(errors_list_length, 1)
        self.assertEqual(specific_error, expected_specific_error)
        self.assertEqual(error_field, expected_error_field)

    @patch('api.geocoding.requests.get')
    def test_moderation_event_created_with_valid_data(
            self,
            mock_get):
        mock_get.return_value = Mock(ok=True, status_code=200)
        mock_get.return_value.json.return_value = geocoding_data

        valid_req_body = json.dumps({
            'source': 'SLC',
            'name': 'Blue Horizon Facility',
            'address': '990 Spring Garden St., Philadelphia PA 19123',
            'country': 'US',
            'location_type': 'Coating',
            'coordinates': {
                'lat': 51.078389,
                'lng': 16.978477
            }
        })

        response = self.client.post(
            self.url,
            valid_req_body,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 202)

        response_body_dict = json.loads(response.content)
        response_moderation_id = response_body_dict.get('moderation_id')
        moderation_event = ModerationEvent.objects.get(
            pk=response_moderation_id
        )
        stringified_created_at = moderation_event.created_at.strftime(
            '%Y-%m-%dT%H:%M:%S.%f'
        ) + 'Z'

        # Check the response.
        self.assertEqual(
            response_body_dict.get('moderation_status'),
            'PENDING'
        )
        self.assertEqual(
            response_body_dict.get('created_at'),
            stringified_created_at
        )
        self.assertEqual(
            response_moderation_id,
            str(moderation_event.uuid)
        )
        self.assertIn("cleaned_data", response_body_dict)
        self.assertEqual(len(response_body_dict), 4)

    @patch('api.geocoding.requests.get')
    def test_moderation_event_not_created_with_invalid_data(
            self,
            mock_get):
        mock_get.return_value = Mock(ok=True, status_code=200)
        mock_get.return_value.json.return_value = geocoding_data

        expected_response_body = {
            'detail': 'The request body is invalid.',
            'errors': [
                {
                    'field': 'sector',
                    'detail': ('Expected value for sector to be a string or a '
                               "list of strings but got {'some_key': 1135}.")
                },
                {
                    'field': 'location_type',
                    'detail': (
                        'Expected value for location_type to be a '
                        'string or a list of strings but got '
                        "{'some_key': 1135}."
                    )
                }
            ]
        }
        initial_moderation_event_count = ModerationEvent.objects.count()

        invalid_req_body = json.dumps({
            'source': 'API',
            'name': 'Blue Horizon Facility',
            'address': '990 Spring Garden St., Philadelphia PA 19123',
            'country': 'US',
            'sector': {'some_key': 1135},
            'parent_company': 'string',
            'product_type': [
                'string'
            ],
            'location_type': {'some_key': 1135},
            'processing_type': [
                'string'
            ],
            'number_of_workers': {
                'min': 0,
                'max': 0
            },
            'coordinates': {
                'lat': 10,
                'lng': 20
            }
        })

        response = self.client.post(
            self.url,
            invalid_req_body,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 422)

        response_body_dict = json.loads(response.content)
        self.assertEqual(response_body_dict, expected_response_body)
        # Ensure that no ModerationEvent record has been created.
        self.assertEqual(ModerationEvent.objects.count(),
                         initial_moderation_event_count)

import json

from unittest.mock import Mock, patch
from rest_framework.test import APITestCase
from django.urls import reverse
from django.core import mail
from allauth.account.models import EmailAddress
from django.contrib.gis.geos import Point
from waffle.testutils import override_switch
from rest_framework import status

from api.models.moderation_event import ModerationEvent
from api.models.contributor.contributor import Contributor
from api.models.facility.facility_list import FacilityList
from api.models.facility.facility_list_item import FacilityListItem
from api.models.source import Source
from api.models.user import User
from api.models.facility.facility import Facility
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

        contributor = Contributor.objects.create(
            admin=self.user,
            name='test contributor 1',
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )

        self.login(user_email, user_password)

        list = FacilityList.objects.create(
            header='header', file_name='one', name='New List Test'
        )
        source = Source.objects.create(
            source_type=Source.LIST,
            facility_list=list,
            contributor=contributor
        )
        list_item = FacilityListItem.objects.create(
            name='Gamma Tech Manufacturing Plant',
            address='1574 Quantum Avenue, Building 4B, Technopolis',
            country_code='YT',
            sector=['Apparel'],
            row_index=1,
            status=FacilityListItem.CONFIRMED_MATCH,
            source=source,
        )
        self.production_location = Facility.objects.create(
            name=list_item.name,
            address=list_item.address,
            country_code=list_item.country_code,
            location=Point(0, 0),
            created_from=list_item
        )

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
        for i in range(30):
            dynamic_valid_req_body = json.dumps({
                'name': f'Blue Horizon Facility {i}',
                'address': '990 Spring Garden St., Philadelphia PA 19123',
                'country': 'US'
            })
            response = self.client.post(
                self.url,
                dynamic_valid_req_body,
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

    @patch('api.geocoding.requests.get')
    def test_duplicate_throttling_is_applied(self, mock_get):
        mock_get.return_value = Mock(ok=True, status_code=200)
        mock_get.return_value.json.return_value = geocoding_data

        # Simulate 2 duplicate requests.
        # First should be successfull.
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

        # Second should be throttled.
        throttled_response = self.client.post(
            self.url,
            self.common_valid_req_body,
            content_type='application/json'
        )
        throttled_response_body_dict = json.loads(throttled_response.content)
        self.assertEqual(throttled_response.status_code, 429)
        self.assertEqual(len(throttled_response_body_dict), 1)
        self.assertEqual(
            throttled_response_body_dict["detail"],
            "Duplicate request submitted, please try again later."
        )

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
            'The request body is invalid.'
        )
        expected_error_field = ('Invalid data. Expected a dictionary '
                                '(object), but got list.')

        response = self.client.post(
            self.url,
            [1, 2, 3],
            content_type='application/json'
        )
        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST)

        response_body_dict = json.loads(response.content)
        self.assertEqual(len(response_body_dict), 2)

        general_error = response_body_dict['detail']
        errors_list_length = len(response_body_dict['errors'])
        specific_error = response_body_dict['detail']
        error_field = response_body_dict['errors'][0]['detail']
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
        email = mail.outbox[0]
        self.assertEqual(
            email.subject,
            "Thank You for Your Submission – "
            "Your Data Is Now Being Reviewed"
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
                    'detail':
                        (
                            'Field sector must be '
                            'a string or a list of strings.'
                        )
                },
                {
                    'field': 'location_type',
                    'detail': (
                        'Field location_type must be a string'
                        ' or a list of strings.'
                    )
                },
                {
                    'field': 'number_of_workers',
                    'errors': [
                        {
                            'field': 'min',
                            'detail': (
                                'Ensure this value is greater than'
                                ' or equal to 1.'
                            )
                        },
                        {
                            'field': 'max',
                            'detail': (
                                'Ensure this value is greater than'
                                ' or equal to 1.'
                            )
                        }
                    ]
                }
            ]
         }
        initial_moderation_event_count = ModerationEvent.objects.count()

        invalid_req_body = json.dumps({
            'source': 'API',
            'name': 'Blue Horizon Facility',
            'address': '990 Spring Garden St., Philadelphia PA 19123',
            'country': 'US',
            'sector': {
                'some_key': 1135
            },
            'parent_company': 'string',
            'product_type': [
                'string'
            ],
            'location_type': {
                'some_key': 1135
            },
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
        self.assertEqual(response.status_code,
                         status.HTTP_422_UNPROCESSABLE_ENTITY)

        response_body_dict = json.loads(response.content)
        self.assertEqual(response_body_dict, expected_response_body)
        # Ensure that no ModerationEvent record has been created.
        self.assertEqual(ModerationEvent.objects.count(),
                         initial_moderation_event_count)

    @patch('api.geocoding.requests.get')
    def test_moderation_event_not_created_with_invalid_parent_company(
            self,
            mock_get):
        mock_get.return_value = Mock(ok=True, status_code=200)
        mock_get.return_value.json.return_value = geocoding_data

        expected_response_body = {
            'detail': 'The request body is invalid.',
            'errors': [
                {
                    'field': 'parent_company',
                    'detail': (
                        'Field parent_company must be a string,'
                        ' not a number.'
                    )
                },
            ]
         }
        initial_moderation_event_count = ModerationEvent.objects.count()

        invalid_req_body = json.dumps({
            'source': 'API',
            'name': 'Blue Horizon Facility',
            'address': '990 Spring Garden St., Philadelphia PA 19123',
            'country': 'US',
            'parent_company': 12345,
        })

        response = self.client.post(
            self.url,
            invalid_req_body,
            content_type='application/json'
        )
        self.assertEqual(response.status_code,
                         status.HTTP_422_UNPROCESSABLE_ENTITY)

        response_body_dict = json.loads(response.content)
        self.assertEqual(response_body_dict, expected_response_body)
        self.assertEqual(ModerationEvent.objects.count(),
                         initial_moderation_event_count)

    @patch('api.geocoding.requests.get')
    def test_moderation_event_created_with_valid_char_field(
            self,
            mock_get):
        mock_get.return_value = Mock(ok=True, status_code=200)
        mock_get.return_value.json.return_value = geocoding_data

        special_characters = '&@, \' _ #()'
        numbers = '1234567890'
        multi_lang_letters = '贾建龙ÖrmeTİCіїъыParentCompanyการผลิตהפָקָהผลิต'
        valid_char_field = (
            special_characters +
            numbers +
            multi_lang_letters
        )

        valid_req_body = json.dumps({
            'source': 'SLC',
            'name': valid_char_field,
            'address': '990 Spring Garden St., Philadelphia PA 19123',
            'country': 'US',
            'parent_company': valid_char_field
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
        name = (
            response_body_dict
            .get('cleaned_data', {})
            .get('name')
        )
        parent_company = (
            response_body_dict
            .get('cleaned_data', {})
            .get('fields', {})
            .get('parent_company')
        )
        self.assertEqual(len(response_body_dict), 4)
        self.assertEqual(name, valid_char_field)
        self.assertEqual(parent_company, valid_char_field)

    @patch('api.geocoding.requests.get')
    def test_moderation_event_created_with_valid_additional_ids(
        self, mock_get
    ):
        mock_get.return_value = Mock(ok=True, status_code=200)
        mock_get.return_value.json.return_value = geocoding_data

        valid_req_body = json.dumps(
            {
                'source': 'SLC',
                'name': 'Blue Horizon Facility',
                'address': '990 Spring Garden St., Philadelphia PA 19123',
                'country': 'US',
                'duns_id': '123456789',
                'lei_id': '12345678901234567890',
                'rba_id': '1234567890123456789012345678901234567890',
            }
        )

        response = self.client.post(
            self.url, valid_req_body, content_type='application/json'
        )
        self.assertEqual(response.status_code, 202)

        response_body_dict = json.loads(response.content)
        response_moderation_id = response_body_dict.get('moderation_id')
        moderation_event = ModerationEvent.objects.get(
            pk=response_moderation_id
        )

        self.assertEqual(
            response_body_dict.get('moderation_status'), 'PENDING'
        )
        self.assertEqual(response_moderation_id, str(moderation_event.uuid))
        self.assertIn("cleaned_data", response_body_dict)
        self.assertEqual(len(response_body_dict), 4)
        self.assertIn('duns_id', moderation_event.cleaned_data['raw_json'])
        self.assertIn('lei_id', moderation_event.cleaned_data['raw_json'])
        self.assertIn('rba_id', moderation_event.cleaned_data['raw_json'])
        self.assertIn("lei_id", moderation_event.cleaned_data['fields'])

        self.assertEqual(
            moderation_event.cleaned_data['fields']['lei_id'],
            '12345678901234567890',
        )
        self.assertIn("rba_id", moderation_event.cleaned_data['fields'])
        self.assertEqual(
            moderation_event.cleaned_data['fields']['rba_id'],
            '1234567890123456789012345678901234567890',
        )
        self.assertIn("duns_id", moderation_event.cleaned_data['fields'])
        self.assertEqual(
            moderation_event.cleaned_data['fields']['duns_id'], '123456789'
        )

    @patch('api.geocoding.requests.get')
    def test_moderation_event_created_with_valid_parent_company_os_id(
        self, mock_get
    ):
        mock_get.return_value = Mock(ok=True, status_code=200)
        mock_get.return_value.json.return_value = geocoding_data

        valid_req_body = json.dumps(
            {
                'source': 'SLC',
                'name': 'Lenexa',
                'address': '9700 Commerce Parkway',
                'country': 'US',
                'parent_company_os_id': [self.production_location.id],
            }
        )

        response = self.client.post(
            self.url, valid_req_body, content_type='application/json'
        )
        self.assertEqual(response.status_code, 202)

        response_body_dict = json.loads(response.content)
        response_moderation_id = response_body_dict.get('moderation_id')
        moderation_event = ModerationEvent.objects.get(
            pk=response_moderation_id
        )

        self.assertEqual(
            response_body_dict.get('moderation_status'), 'PENDING'
        )
        self.assertEqual(response_moderation_id, str(moderation_event.uuid))
        self.assertIn("cleaned_data", response_body_dict)
        self.assertIn('parent_company_os_id',
                      moderation_event.cleaned_data['raw_json'])
        self.assertIn("parent_company_os_id",
                      moderation_event.cleaned_data['fields'])

        self.assertEqual(
            moderation_event.cleaned_data['fields']['parent_company_os_id'],
            [self.production_location.id],
        )

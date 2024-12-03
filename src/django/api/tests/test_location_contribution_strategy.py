import unittest
from unittest.mock import Mock, patch
from rest_framework.test import APITestCase

from api.models.moderation_event import ModerationEvent
from api.models.contributor.contributor import Contributor
from api.models.user import User
from api.tests.test_data import (
    geocoding_data,
    geocoding_no_results
)
from api.moderation_event_actions.creation.moderation_event_creator \
    import ModerationEventCreator
from api.moderation_event_actions.creation.location_contribution \
    .location_contribution import LocationContribution
from api.moderation_event_actions.creation.dtos.create_moderation_event_dto \
    import CreateModerationEventDTO
from contricleaner.lib.contri_cleaner import ContriCleaner
from contricleaner.lib.exceptions.handler_not_set_error \
    import HandlerNotSetError


class TestLocationContributionStrategy(APITestCase):
    def setUp(self):
        self.common_valid_input_data = {
            'name': 'Blue Horizon Facility',
            'address': '990 Spring Garden St., Philadelphia PA 19123',
            'country': 'US'
        }

        user_email = 'test@example.com'
        user_password = 'example123'
        user = User.objects.create(email=user_email)
        user.set_password(user_password)
        user.save()

        self.contributor = Contributor.objects.create(
            admin=user,
            name='test contributor 1',
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )

        location_contribution_strategy = LocationContribution()
        self.moderation_event_creator = ModerationEventCreator(
            location_contribution_strategy
        )

    @patch('api.geocoding.requests.get')
    def test_source_set_as_api_regardless_of_whether_passed(self, mock_get):
        mock_get.return_value = Mock(ok=True, status_code=200)
        mock_get.return_value.json.return_value = geocoding_data

        self.assertNotIn('source', self.common_valid_input_data)

        event_dto = CreateModerationEventDTO(
            contributor_id=self.contributor,
            raw_data=self.common_valid_input_data,
            request_type=ModerationEvent.RequestType.CREATE.value
        )
        result = self.moderation_event_creator.perform_event_creation(
            event_dto
        )

        self.assertEqual(result.status_code, 202)
        self.assertEqual(result.moderation_event.source, 'API')

    @patch('api.geocoding.requests.get')
    def test_invalid_source_value_cannot_be_accepted(self, mock_get):
        mock_get.return_value = Mock(ok=True, status_code=200)
        mock_get.return_value.json.return_value = geocoding_data

        invalid_input_data_1 = {
            'source': 'invalid_SLC',
            'name': 'Blue Horizon Facility',
            'address': '990 Spring Garden St., Philadelphia PA 19123',
            'country': 'US'
        }
        invalid_input_data_2 = {
            'source': 'R8',
            'name': 'Blue Horizon Facility',
            'address': '990 Spring Garden St., Philadelphia PA 19123',
            'country': 'US'
        }
        invalid_input_data_3 = {
            'source': ['An item in the list'],
            'name': 'Blue Horizon Facility',
            'address': '990 Spring Garden St., Philadelphia PA 19123',
            'country': 'US'
        }

        expected_error_result_1 = {
            'detail': 'The request body is invalid.',
            'errors': [
                {
                    'field': 'source',
                    'detail': ('Ensure this field has no more than 3 '
                               'characters.')
                }
            ]
        }
        expected_error_result_2 = {
            'detail': 'The request body is invalid.',
            'errors': [
                {
                    'field': 'source',
                    'detail': ('The source value should be one of the '
                               'following: API, SLC.')
                }
            ]
        }
        expected_error_result_3 = {
            'detail': 'The request body is invalid.',
            'errors': [
                {
                    'field': 'source',
                    'detail': 'Not a valid string.'
                }
            ]
        }

        # Check the length validation.
        event_dto_1 = CreateModerationEventDTO(
            contributor_id=self.contributor,
            raw_data=invalid_input_data_1,
            request_type=ModerationEvent.RequestType.CREATE.value
        )
        result_1 = self.moderation_event_creator.perform_event_creation(
            event_dto_1
        )
        self.assertEqual(result_1.status_code, 422)
        self.assertEqual(result_1.errors, expected_error_result_1)
        self.assertIsNone(result_1.moderation_event)

        # Check validation of accepted values.
        event_dto_2 = CreateModerationEventDTO(
            contributor_id=self.contributor,
            raw_data=invalid_input_data_2,
            request_type=ModerationEvent.RequestType.CREATE.value
        )
        result_2 = self.moderation_event_creator.perform_event_creation(
            event_dto_2
        )
        self.assertEqual(result_2.status_code, 422)
        self.assertEqual(result_2.errors, expected_error_result_2)
        self.assertIsNone(result_2.moderation_event)

        # Check the accepted data type validation for the source field.
        event_dto_3 = CreateModerationEventDTO(
            contributor_id=self.contributor,
            raw_data=invalid_input_data_3,
            request_type=ModerationEvent.RequestType.CREATE.value
        )
        result_3 = self.moderation_event_creator.perform_event_creation(
            event_dto_3
        )
        self.assertEqual(result_3.status_code, 422)
        self.assertEqual(result_3.errors, expected_error_result_3)
        self.assertIsNone(result_3.moderation_event)

    def test_mapping_of_unsupported_fields_by_contricleaner_with_valid_data(
            self):
        input_data = {
            'source': 'API',
            'name': 'Blue Horizon Facility',
            'address': '990 Spring Garden St., Philadelphia PA 19123',
            'country': 'US',
            'location_type': ['Coating'],
            'coordinates': {
                'lat': 51.078389,
                'lng': 16.978477
            }
        }

        event_dto = CreateModerationEventDTO(
            contributor_id=self.contributor,
            raw_data=input_data,
            request_type=ModerationEvent.RequestType.CREATE.value
        )
        result = self.moderation_event_creator.perform_event_creation(
            event_dto
        )
        self.assertEqual(result.status_code, 202)
        self.assertIsNotNone(result.moderation_event)

        # Check that ContriCleaner recognizes the mapped fields and that they
        # are saved with their original names and the same values as defined
        # for the corresponding keys that follow the API v1 naming convention.
        moderation_event = result.moderation_event

        self.assertIn('facility_type', moderation_event.cleaned_data['fields'])
        self.assertEqual(
            input_data['location_type'],
            moderation_event.cleaned_data['fields']
            ['facility_type']['raw_values']
        )

        self.assertIn('lat', moderation_event.cleaned_data['fields'])
        self.assertEqual(
            input_data['coordinates']['lat'],
            moderation_event.cleaned_data['fields']['lat']
        )
        self.assertIn('lng', moderation_event.cleaned_data['fields'])
        self.assertEqual(
            input_data['coordinates']['lng'],
            moderation_event.cleaned_data['fields']['lng']
        )

    def test_mapping_of_unsupported_fields_by_contricleaner_with_invalid_data(
            self):
        expected_error_result = {
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
                        "{'key': 'Coating'}."
                    )
                }
            ]
        }
        input_data = {
            'source': 'API',
            'name': 'Blue Horizon Facility',
            'address': '990 Spring Garden St., Philadelphia PA 19123',
            'country': 'US',
            'location_type': {'key': 'Coating'},
            'sector': {'some_key': 1135},
            'coordinates': {
                'lat': 51.078389,
                'lng': 16.978477
            }
        }

        event_dto = CreateModerationEventDTO(
            contributor_id=self.contributor,
            raw_data=input_data,
            request_type=ModerationEvent.RequestType.CREATE.value
        )
        result = self.moderation_event_creator.perform_event_creation(
            event_dto
        )
        self.assertEqual(result.status_code, 422)
        self.assertIsNone(result.moderation_event)

        # Check that ContriCleaner recognizes the mapped fields and that
        # ContriCleaner errors for these fields are transformed, including
        # both the field and the error message, according to the API v1 naming
        # convention. Also, double-check that errors for supported fields are
        # skipped during mapping but are transformed at the same time, since
        # ContriCleaner has its own structure for the error object.
        self.assertEqual(result.errors, expected_error_result)

    def test_handling_of_cc_list_level_errors(self):
        expected_general_error = 'The request body is invalid.'
        # Expect only part of the message, as the next part is dynamic because
        # it is generated from a Python set and is hard to predict.
        expected_part_of_specific_error = 'Required Fields are missing:'
        expected_error_field = 'non_field_errors'
        input_data = {
            'source': 'SLC',
            'coordinates': {
                'lat': 51.078389,
                'lng': 16.978477
            }
        }

        event_dto = CreateModerationEventDTO(
            contributor_id=self.contributor,
            raw_data=input_data,
            request_type=ModerationEvent.RequestType.CREATE.value
        )
        result = self.moderation_event_creator.perform_event_creation(
            event_dto
        )
        self.assertEqual(result.status_code, 422)
        self.assertIsNone(result.moderation_event)
        self.assertEqual(len(result.errors), 2)
        self.assertEqual(result.errors['detail'], expected_general_error)
        self.assertIn(
            expected_part_of_specific_error,
            result.errors['errors'][0]['detail']
        )
        self.assertEqual(
            result.errors['errors'][0]['field'],
            expected_error_field
        )

    @patch.object(ContriCleaner, 'process_data')
    def test_handling_of_cc_handler_not_set_exception(self, mock_process_data):
        mock_process_data.side_effect = HandlerNotSetError(
            "Next Handler wasn't set."
        )
        expected_error_result = {
            'detail': ('An unexpected error occurred while processing the '
                       'request.')
        }

        input_data = {
            'source': 'API',
            'name': 'Blue Horizon Facility',
            'address': '990 Spring Garden St., Philadelphia PA 19123',
            'country': 'US',
            'location_type': ['Coating'],
            'coordinates': {
                'lat': 51.078389,
                'lng': 16.978477
            }
        }

        event_dto = CreateModerationEventDTO(
            contributor_id=self.contributor,
            raw_data=input_data,
            request_type=ModerationEvent.RequestType.CREATE.value
        )
        result = self.moderation_event_creator.perform_event_creation(
            event_dto
        )
        self.assertEqual(result.status_code, 500)
        self.assertIsNone(result.moderation_event)
        self.assertEqual(result.errors, expected_error_result)

    @patch('api.geocoding.requests.get')
    def test_handling_geocoded_no_results_error(self, mock_get):
        mock_get.return_value = Mock(ok=True, status_code=200)
        mock_get.return_value.json.return_value = geocoding_no_results
        expected_error_result = {
            'detail': 'The request body is invalid.',
            'errors': [
                {
                    'field': 'non_field_errors',
                    "detail": ('A valid address could not be found for the '
                               'provided country and address. This may be due '
                               'to incorrect, incomplete, or ambiguous '
                               'information. Please verify and try again.')
                }
            ]
        }

        input_data = {
            'source': 'API',
            'name': 'Blue Ocean',
            'address': 'Atlantis, Ocean, Underwater',
            'country': 'UK'
        }

        event_dto = CreateModerationEventDTO(
            contributor_id=self.contributor,
            raw_data=input_data,
            request_type=ModerationEvent.RequestType.CREATE.value
        )
        result = self.moderation_event_creator.perform_event_creation(
            event_dto
        )
        self.assertEqual(result.status_code, 422)
        self.assertIsNone(result.moderation_event)
        self.assertEqual(result.errors, expected_error_result)

    @patch(('api.moderation_event_actions.creation.location_contribution.'
            'processors.geocoding_processor.geocode_address'))
    def test_handling_geocoding_internal_error(self, mock_geocode_address):
        mock_geocode_address.side_effect = ValueError('An error occurred.')
        expected_error_result = {
            'detail': (
                'An unexpected error occurred while processing the request.'
            )
        }

        input_data = {
            'source': 'API',
            'name': 'Blue Ocean',
            'address': 'Atlantis, Ocean, Underwater',
            'country': 'UK'
        }

        event_dto = CreateModerationEventDTO(
            contributor_id=self.contributor,
            raw_data=input_data,
            request_type=ModerationEvent.RequestType.CREATE.value
        )
        result = self.moderation_event_creator.perform_event_creation(
            event_dto
        )
        self.assertEqual(result.status_code, 500)
        self.assertIsNone(result.moderation_event)
        self.assertEqual(result.errors, expected_error_result)

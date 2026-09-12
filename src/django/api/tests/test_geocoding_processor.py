from unittest.mock import patch

import requests
from django.test import TestCase
from rest_framework import status

from api.constants import APIV1CommonErrorMessages
from api.models.moderation_event import ModerationEvent
from api.moderation_event_actions.creation.dtos.create_moderation_event_dto \
    import CreateModerationEventDTO
from api.moderation_event_actions.creation.location_contribution \
    .processors.geocoding_processor import GeocodingProcessor
from api.tests.test_data import geocoding_data


class TestGeocodingProcessor(TestCase):
    def setUp(self):
        self.processor = GeocodingProcessor()

    def _make_event_dto(self):
        return CreateModerationEventDTO(
            contributor=None,
            raw_data={},
            request_type=ModerationEvent.RequestType.CREATE.value,
            cleaned_data={
                'fields': {},
                'address': '990 Spring Garden St, Philadelphia PA 19123',
                'country_code': 'US',
            },
        )

    @patch('api.geocoding.requests.get')
    def test_successful_geocode_sets_geocode_result(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = geocoding_data

        result = self.processor.process(self._make_event_dto())

        self.assertEqual(result.errors, {})
        self.assertIn('geocoded_point', result.geocode_result)

    @patch('api.geocoding.requests.get')
    def test_non_200_response_is_reported_as_internal_error(self, mock_get):
        mock_get.return_value.status_code = 400

        result = self.processor.process(self._make_event_dto())

        self.assertEqual(
            result.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        self.assertEqual(
            result.errors['detail'],
            APIV1CommonErrorMessages.COMMON_INTERNAL_ERROR
        )

    @patch('api.geocoding.requests.get')
    def test_timed_out_request_is_reported_as_internal_error(self, mock_get):
        mock_get.side_effect = requests.exceptions.Timeout()

        result = self.processor.process(self._make_event_dto())

        self.assertEqual(
            result.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        self.assertEqual(
            result.errors['detail'],
            APIV1CommonErrorMessages.COMMON_INTERNAL_ERROR
        )

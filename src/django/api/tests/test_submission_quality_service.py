from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.test import TestCase

from api.services.submission_quality_service import (
    SubmissionQualityService,
    SubmissionQualityVerdicts,
)


def _tool_use_block(data):
    return SimpleNamespace(type='tool_use', input=data)


def _valid_input(flagged=False, reason=''):
    verdict = {'flagged': flagged, 'reason': reason}
    return {
        'name_quality': dict(verdict),
        'address_quality': dict(verdict),
        'address_country_mismatch': dict(verdict),
        'multiple_locations': dict(verdict),
    }


class TestSubmissionQualityService(TestCase):
    def setUp(self):
        # Avoid constructing a real AnthropicBedrock client (which would
        # resolve AWS credentials); each test swaps in its own fake
        # response for messages.create.
        with patch(
            'api.services.submission_quality_service.AnthropicBedrock'
        ):
            self.service = SubmissionQualityService()
        self.service._client = MagicMock()

    def _evaluate_with_response(self, response):
        self.service._client.messages.create.return_value = response
        return self.service.evaluate(
            name='Blue Horizon Facility',
            address='990 Spring Garden St., Philadelphia PA 19123',
            country_name='United States',
        )

    def test_valid_response_is_parsed(self):
        response = SimpleNamespace(
            content=[_tool_use_block(_valid_input(flagged=True, reason='x'))]
        )
        verdicts = self._evaluate_with_response(response)

        self.assertIsInstance(verdicts, SubmissionQualityVerdicts)
        self.assertTrue(verdicts.name_quality.flagged)
        self.assertEqual(verdicts.name_quality.reason, 'x')

    def test_no_tool_use_block_fails_open(self):
        response = SimpleNamespace(
            content=[SimpleNamespace(type='text', text='hello')]
        )
        self.assertIsNone(self._evaluate_with_response(response))

    def test_empty_content_fails_open(self):
        response = SimpleNamespace(content=[])
        self.assertIsNone(self._evaluate_with_response(response))

    def test_missing_content_attribute_fails_open(self):
        # An unexpected response object without .content must not raise.
        response = SimpleNamespace()
        self.assertIsNone(self._evaluate_with_response(response))

    def test_missing_verdict_field_fails_open(self):
        data = _valid_input()
        del data['name_quality']['reason']
        response = SimpleNamespace(content=[_tool_use_block(data)])
        self.assertIsNone(self._evaluate_with_response(response))

    def test_missing_check_key_fails_open(self):
        data = _valid_input()
        del data['multiple_locations']
        response = SimpleNamespace(content=[_tool_use_block(data)])
        self.assertIsNone(self._evaluate_with_response(response))

    def test_non_bool_flagged_fails_open(self):
        data = _valid_input()
        data['name_quality']['flagged'] = 'true'
        response = SimpleNamespace(content=[_tool_use_block(data)])
        self.assertIsNone(self._evaluate_with_response(response))

    def test_non_str_reason_fails_open(self):
        data = _valid_input()
        data['address_quality']['reason'] = None
        response = SimpleNamespace(content=[_tool_use_block(data)])
        self.assertIsNone(self._evaluate_with_response(response))

    def test_client_error_fails_open(self):
        self.service._client.messages.create.side_effect = RuntimeError(
            'bedrock unavailable'
        )
        result = self.service.evaluate(
            name='n', address='a', country_name='c'
        )
        self.assertIsNone(result)

import os
from unittest.mock import patch

from django.test import TestCase
from pydantic_ai import models
from pydantic_ai.messages import ModelResponse, TextPart
from pydantic_ai.models.function import FunctionModel
from pydantic_ai.models.test import TestModel

from api.services.claim_quality_service import (
    _DEFAULT_INSTRUCTIONS,
    ClaimQualityService,
    ClaimQualityVerdicts,
)

# No test below should ever reach a real model endpoint; pydantic-ai
# raises instead of making a network call if one slips through.
models.ALLOW_MODEL_REQUESTS = False

# The base class imports boto3 and Agent; patch targets live there.
_BASE_MODULE = 'api.services.submission_quality_service'


def _valid_output(flagged=False, reason=''):
    verdict = {'flagged': flagged, 'reason': reason}
    return {
        'name_quality': dict(verdict),
        'address_quality': dict(verdict),
        'address_country_mismatch': dict(verdict),
        'multiple_locations': dict(verdict),
        'different_location': dict(verdict),
    }


def _raise_runtime_error(messages, info):
    raise RuntimeError('bedrock unavailable')


def _text_only_response(messages, info):
    return ModelResponse(parts=[TextPart('hello')])


class TestClaimQualityService(TestCase):
    def setUp(self):
        with patch(f'{_BASE_MODULE}.boto3'):
            self.service = ClaimQualityService()
            self.service._get_agent()

    def _evaluate_with_model(self, model):
        with self.service._agent.override(model=model):
            return self.service.evaluate(
                name='Blue Horizon Facility',
                address='990 Spring Garden St., Philadelphia PA 19123',
                country_name='United States',
                current_name='Blue Horizon',
                current_address='990 Spring Garden Street, Philadelphia',
            )

    def test_valid_output_is_parsed_including_different_location(self):
        data = _valid_output()
        data['different_location'] = {
            'flagged': True, 'reason': 'Another city entirely.'
        }
        verdicts = self._evaluate_with_model(
            TestModel(custom_output_args=data)
        )

        self.assertIsInstance(verdicts, ClaimQualityVerdicts)
        self.assertFalse(verdicts.name_quality.flagged)
        self.assertTrue(verdicts.different_location.flagged)
        self.assertEqual(
            verdicts.different_location.reason, 'Another city entirely.'
        )

    def test_missing_different_location_fails_open(self):
        # The SLC schema's four checks alone are not a valid claim
        # verdict: the extra check is required, not optional.
        data = _valid_output()
        del data['different_location']
        result = self._evaluate_with_model(TestModel(custom_output_args=data))
        self.assertIsNone(result)

    def test_text_only_response_fails_open(self):
        result = self._evaluate_with_model(FunctionModel(_text_only_response))
        self.assertIsNone(result)

    def test_model_error_fails_open_and_logs_with_claim_label(self):
        # The fail-open line keeps the text the CloudWatch metric filter
        # matches (see deployment/terraform/alarms.tf) and tags the
        # check so the two callers can be told apart in Logs Insights.
        with self.assertLogs(_BASE_MODULE, level='ERROR') as logs:
            result = self._evaluate_with_model(
                FunctionModel(_raise_runtime_error)
            )
        self.assertIsNone(result)
        self.assertTrue(any(
            'Submission quality check failed; skipping (fail open). '
            'check=claim' in line
            for line in logs.output
        ))

    def test_token_usage_is_logged_with_claim_label(self):
        with self.assertLogs(_BASE_MODULE, level='INFO') as logs:
            self._evaluate_with_model(
                TestModel(custom_output_args=_valid_output())
            )
        self.assertTrue(any(
            'Submission quality check tokens' in line
            and 'check=claim' in line
            for line in logs.output
        ))

    def test_prompt_carries_claimed_and_listed_values(self):
        captured = {}

        def capture(messages, info):
            captured['prompt'] = messages[-1].parts[-1].content
            raise RuntimeError('captured; stop the run')

        self._evaluate_with_model(FunctionModel(capture))

        prompt = captured['prompt']
        self.assertIn('Claimed name: Blue Horizon Facility', prompt)
        self.assertIn(
            'Claimed address: 990 Spring Garden St., Philadelphia PA 19123',
            prompt,
        )
        self.assertIn('Country: United States', prompt)
        self.assertIn('Currently listed name: Blue Horizon', prompt)
        self.assertIn(
            'Currently listed address: 990 Spring Garden Street, '
            'Philadelphia',
            prompt,
        )

    def _instructions_sent_to_model(self, env_value):
        env = {'CLAIM_QUALITY_INSTRUCTIONS': env_value}
        with patch.dict(os.environ, env), patch(f'{_BASE_MODULE}.boto3'):
            service = ClaimQualityService()
            service._get_agent()

        captured = {}

        def capture(messages, info):
            captured['instructions'] = messages[-1].instructions
            raise RuntimeError('captured; stop the run')

        with service._agent.override(model=FunctionModel(capture)):
            service.evaluate(
                name='n', address='a', country_name='c',
                current_name='cn', current_address='ca',
            )
        return captured['instructions']

    def test_instructions_env_var_overrides_default(self):
        self.assertEqual(
            self._instructions_sent_to_model('Be extremely lenient.'),
            'Be extremely lenient.',
        )

    def test_empty_instructions_env_var_falls_back_to_default(self):
        self.assertEqual(
            self._instructions_sent_to_model(''),
            _DEFAULT_INSTRUCTIONS,
        )

    def test_slc_instructions_env_var_does_not_leak_into_claim_check(self):
        env = {
            'SUBMISSION_QUALITY_INSTRUCTIONS': 'SLC framing.',
            'CLAIM_QUALITY_INSTRUCTIONS': '',
        }
        with patch.dict(os.environ, env), patch(f'{_BASE_MODULE}.boto3'):
            service = ClaimQualityService()
            service._get_agent()

        captured = {}

        def capture(messages, info):
            captured['instructions'] = messages[-1].instructions
            raise RuntimeError('captured; stop the run')

        with service._agent.override(model=FunctionModel(capture)):
            service.evaluate(
                name='n', address='a', country_name='c',
                current_name='cn', current_address='ca',
            )
        self.assertEqual(captured['instructions'], _DEFAULT_INSTRUCTIONS)

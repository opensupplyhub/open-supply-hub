import os
from unittest.mock import patch

from django.test import TestCase
from pydantic_ai import models
from pydantic_ai.messages import ModelResponse, TextPart
from pydantic_ai.models.function import FunctionModel
from pydantic_ai.models.test import TestModel

from api.services.submission_quality_service import (
    _DEFAULT_INSTRUCTIONS,
    SubmissionQualityService,
    SubmissionQualityVerdicts,
)

# No test below should ever reach a real model endpoint; pydantic-ai
# raises instead of making a network call if one slips through.
models.ALLOW_MODEL_REQUESTS = False


def _valid_output(flagged=False, reason=''):
    verdict = {'flagged': flagged, 'reason': reason}
    return {
        'name_quality': dict(verdict),
        'address_quality': dict(verdict),
        'address_country_mismatch': dict(verdict),
        'multiple_locations': dict(verdict),
    }


def _raise_runtime_error(messages, info):
    raise RuntimeError('bedrock unavailable')


def _text_only_response(messages, info):
    # A model that answers in prose instead of calling the output tool.
    return ModelResponse(parts=[TextPart('hello')])


class TestSubmissionQualityService(TestCase):
    def setUp(self):
        # Avoid constructing a real bedrock-runtime client (which would
        # resolve AWS credentials); every test overrides the agent's
        # model, so the client is never used.
        with patch('api.services.submission_quality_service.boto3'):
            self.service = SubmissionQualityService()

    def _evaluate_with_model(self, model):
        with self.service._agent.override(model=model):
            return self.service.evaluate(
                name='Blue Horizon Facility',
                address='990 Spring Garden St., Philadelphia PA 19123',
                country_name='United States',
            )

    def test_valid_output_is_parsed(self):
        verdicts = self._evaluate_with_model(
            TestModel(custom_output_args=_valid_output(
                flagged=True, reason='x'
            ))
        )

        self.assertIsInstance(verdicts, SubmissionQualityVerdicts)
        self.assertTrue(verdicts.name_quality.flagged)
        self.assertEqual(verdicts.name_quality.reason, 'x')

    def test_text_only_response_fails_open(self):
        # retries=0 on the agent means a response with no structured
        # output raises inside run_sync instead of re-prompting.
        result = self._evaluate_with_model(FunctionModel(_text_only_response))
        self.assertIsNone(result)

    def test_missing_verdict_field_fails_open(self):
        data = _valid_output()
        del data['name_quality']['reason']
        result = self._evaluate_with_model(TestModel(custom_output_args=data))
        self.assertIsNone(result)

    def test_missing_check_key_fails_open(self):
        data = _valid_output()
        del data['multiple_locations']
        result = self._evaluate_with_model(TestModel(custom_output_args=data))
        self.assertIsNone(result)

    def test_non_bool_flagged_fails_open(self):
        data = _valid_output()
        data['name_quality']['flagged'] = 'not a boolean'
        result = self._evaluate_with_model(TestModel(custom_output_args=data))
        self.assertIsNone(result)

    def test_bool_like_string_flagged_is_coerced(self):
        # pydantic's lax mode accepts unambiguous boolean spellings like
        # 'true'; genuinely non-boolean junk still fails validation (see
        # test_non_bool_flagged_fails_open). Pinned here because it is a
        # deliberate loosening of the previous hand-rolled type guard.
        data = _valid_output()
        data['name_quality']['flagged'] = 'true'
        verdicts = self._evaluate_with_model(
            TestModel(custom_output_args=data)
        )
        self.assertIs(verdicts.name_quality.flagged, True)

    def test_non_str_reason_fails_open(self):
        data = _valid_output()
        data['address_quality']['reason'] = None
        result = self._evaluate_with_model(TestModel(custom_output_args=data))
        self.assertIsNone(result)

    def test_model_error_fails_open(self):
        result = self._evaluate_with_model(FunctionModel(_raise_runtime_error))
        self.assertIsNone(result)

    def _instructions_sent_to_model(self, env_value):
        # Instructions are read at service construction, so build a fresh
        # service under the patched environment, then capture what the
        # agent actually sends to the model. The capture raises so the
        # run stops there; evaluate() failing open is irrelevant here.
        env = {'SUBMISSION_QUALITY_INSTRUCTIONS': env_value}
        with patch.dict(os.environ, env), patch(
            'api.services.submission_quality_service.boto3'
        ):
            service = SubmissionQualityService()

        captured = {}

        def capture(messages, info):
            captured['instructions'] = messages[-1].instructions
            raise RuntimeError('captured; stop the run')

        with service._agent.override(model=FunctionModel(capture)):
            service.evaluate(name='n', address='a', country_name='c')
        return captured['instructions']

    def test_instructions_env_var_overrides_default(self):
        self.assertEqual(
            self._instructions_sent_to_model('Be extremely lenient.'),
            'Be extremely lenient.',
        )

    def test_empty_instructions_env_var_falls_back_to_default(self):
        # .env.sample ships the var set-but-empty; that must mean "use
        # the default", not "send no instructions".
        self.assertEqual(
            self._instructions_sent_to_model(''),
            _DEFAULT_INSTRUCTIONS,
        )

from unittest.mock import patch

from botocore.exceptions import ProfileNotFound
from django.contrib.gis.geos import Point
from rest_framework import status
from rest_framework.test import APITestCase
from waffle.testutils import override_switch

from api.models.moderation_event import ModerationEvent
from api.models.contributor.contributor import Contributor
from api.models.user import User
from api.models.facility.facility import Facility
from api.models.facility.facility_list import FacilityList
from api.models.facility.facility_list_item import FacilityListItem
from api.models.source import Source
from api.moderation_event_actions.creation.moderation_event_creator \
    import ModerationEventCreator
from api.moderation_event_actions.creation.location_contribution \
    .location_contribution import LocationContribution
from api.moderation_event_actions.creation.dtos.create_moderation_event_dto \
    import CreateModerationEventDTO
from api.services.submission_quality_service import (
    QualityVerdict,
    SubmissionQualityVerdicts,
)

CLEAN_VERDICTS = SubmissionQualityVerdicts(
    name_quality=QualityVerdict(flagged=False, reason=''),
    address_quality=QualityVerdict(flagged=False, reason=''),
    address_country_mismatch=QualityVerdict(flagged=False, reason=''),
    multiple_locations=QualityVerdict(flagged=False, reason=''),
)


def _flagged_verdicts(**flagged_types):
    fields = {
        'name_quality': QualityVerdict(flagged=False, reason=''),
        'address_quality': QualityVerdict(flagged=False, reason=''),
        'address_country_mismatch': QualityVerdict(flagged=False, reason=''),
        'multiple_locations': QualityVerdict(flagged=False, reason=''),
    }
    for warning_type, reason in flagged_types.items():
        fields[warning_type] = QualityVerdict(flagged=True, reason=reason)
    return SubmissionQualityVerdicts(**fields)


class TestSubmissionQualityProcessor(APITestCase):
    def setUp(self):
        user = User.objects.create(email='test@example.com')
        user.set_password('example123')
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

        self.base_input_data = {
            'source': 'SLC',
            'name': 'Blue Horizon Facility',
            'address': '990 Spring Garden St., Philadelphia PA 19123',
            'country': 'US',
            'coordinates': {
                'lat': 51.078389,
                'lng': 16.978477
            }
        }

    def _submit(
        self, contributor, input_data, ignore_warnings=False,
        request_type=ModerationEvent.RequestType.CREATE.value, os=None,
    ):
        event_dto = CreateModerationEventDTO(
            contributor=contributor,
            raw_data=input_data,
            request_type=request_type,
            ignore_warnings=ignore_warnings,
            os=os,
        )
        return self.moderation_event_creator.perform_event_creation(
            event_dto
        )

    def _create_existing_facility(self):
        facility_list = FacilityList.objects.create(
            header='header', file_name='one', name='New List Test'
        )
        source = Source.objects.create(
            source_type=Source.LIST,
            facility_list=facility_list,
            contributor=self.contributor
        )
        list_item = FacilityListItem.objects.create(
            name=self.base_input_data['name'],
            address=self.base_input_data['address'],
            country_code=self.base_input_data['country'],
            sector=['Apparel'],
            row_index=1,
            status=FacilityListItem.CONFIRMED_MATCH,
            source=source
        )
        return Facility.objects.create(
            name=list_item.name,
            address=list_item.address,
            country_code=list_item.country_code,
            location=Point(0, 0),
            created_from=list_item
        )

    def _patch_evaluate(self, return_value):
        return patch(
            'api.moderation_event_actions.creation.location_contribution'
            '.processors.submission_quality_processor'
            '.SubmissionQualityService.evaluate',
            return_value=return_value,
        )

    def test_clean_submission_is_not_flagged(self):
        with self._patch_evaluate(CLEAN_VERDICTS):
            result = self._submit(self.contributor, self.base_input_data)

        self.assertEqual(result.status_code, status.HTTP_202_ACCEPTED)
        self.assertIsNotNone(result.moderation_event)

    def test_flagged_name_quality_blocks_creation_with_warning(self):
        verdicts = _flagged_verdicts(
            name_quality='Looks like test data, not a business name.'
        )
        with self._patch_evaluate(verdicts):
            result = self._submit(self.contributor, self.base_input_data)

        self.assertEqual(result.status_code, status.HTTP_409_CONFLICT)
        self.assertIsNone(result.moderation_event)
        warning_types = [w['type'] for w in result.errors['warnings']]
        self.assertEqual(warning_types, ['name_quality'])
        self.assertEqual(
            result.errors['warnings'][0]['message'],
            'Looks like test data, not a business name.'
        )

    def test_multiple_flagged_checks_are_all_returned(self):
        verdicts = _flagged_verdicts(
            name_quality='Looks like test data.',
            address_country_mismatch='Address does not look like US.',
        )
        with self._patch_evaluate(verdicts):
            result = self._submit(self.contributor, self.base_input_data)

        self.assertEqual(result.status_code, status.HTTP_409_CONFLICT)
        self.assertIsNone(result.moderation_event)
        warning_types = {w['type'] for w in result.errors['warnings']}
        self.assertEqual(
            warning_types, {'name_quality', 'address_country_mismatch'}
        )

    def test_ignore_warnings_bypasses_the_check_without_calling_llm(self):
        with self._patch_evaluate(None) as mock_evaluate:
            result = self._submit(
                self.contributor, self.base_input_data,
                ignore_warnings=True,
            )

        mock_evaluate.assert_not_called()
        self.assertEqual(result.status_code, status.HTTP_202_ACCEPTED)
        self.assertIsNotNone(result.moderation_event)

    def test_llm_failure_fails_open(self):
        with self._patch_evaluate(None):
            result = self._submit(self.contributor, self.base_input_data)

        self.assertEqual(result.status_code, status.HTTP_202_ACCEPTED)
        self.assertIsNotNone(result.moderation_event)

    def test_service_construction_failure_fails_open(self):
        # SubmissionQualityService builds its bedrock client lazily
        # inside evaluate()'s fail-open handler, so an environment where
        # the client cannot even be constructed (e.g. ProfileNotFound
        # from a misconfigured BEDROCK_AWS_PROFILE) skips the check
        # instead of aborting the whole submission with an unhandled
        # exception. Unlike the tests above, evaluate() is deliberately
        # not patched here.
        with patch(
            'api.services.submission_quality_service.boto3.session.Session',
            side_effect=ProfileNotFound(profile='nonexistent'),
        ):
            result = self._submit(self.contributor, self.base_input_data)

        self.assertEqual(result.status_code, status.HTTP_202_ACCEPTED)
        self.assertIsNotNone(result.moderation_event)

    def test_non_slc_source_is_never_flagged(self):
        api_input_data = {
            **self.base_input_data,
            'source': ModerationEvent.Source.API.value,
        }
        verdicts = _flagged_verdicts(name_quality='Looks like test data.')
        with self._patch_evaluate(verdicts) as mock_evaluate:
            result = self._submit(self.contributor, api_input_data)

        mock_evaluate.assert_not_called()
        self.assertEqual(result.status_code, status.HTTP_202_ACCEPTED)
        self.assertIsNotNone(result.moderation_event)

    @override_switch('slc_submission_quality_check', active=False)
    def test_switch_off_skips_check_without_calling_llm(self):
        # With the waffle switch off, even a submission the model would
        # flag is created without an LLM call.
        verdicts = _flagged_verdicts(name_quality='Looks like test data.')
        with self._patch_evaluate(verdicts) as mock_evaluate:
            result = self._submit(self.contributor, self.base_input_data)

        mock_evaluate.assert_not_called()
        self.assertEqual(result.status_code, status.HTTP_202_ACCEPTED)
        self.assertIsNotNone(result.moderation_event)

    @override_switch('slc_submission_quality_check', active=True)
    def test_switch_on_still_flags(self):
        # The other tests rely on migration 0226 creating the switch
        # active; this pins the explicit-on state so the pair of switch
        # tests documents both positions.
        verdicts = _flagged_verdicts(name_quality='Looks like test data.')
        with self._patch_evaluate(verdicts):
            result = self._submit(self.contributor, self.base_input_data)

        self.assertEqual(result.status_code, status.HTTP_409_CONFLICT)
        self.assertIsNone(result.moderation_event)

    def test_update_request_type_is_never_flagged(self):
        existing_facility = self._create_existing_facility()
        verdicts = _flagged_verdicts(name_quality='Looks like test data.')
        with self._patch_evaluate(verdicts) as mock_evaluate:
            result = self._submit(
                self.contributor,
                self.base_input_data,
                request_type=ModerationEvent.RequestType.UPDATE.value,
                os=existing_facility,
            )

        mock_evaluate.assert_not_called()
        self.assertNotEqual(result.status_code, status.HTTP_409_CONFLICT)

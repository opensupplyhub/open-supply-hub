import logging

from rest_framework import status

from api.moderation_event_actions.creation.location_contribution \
    .processors.contribution_processor import ContributionProcessor
from api.moderation_event_actions.creation.dtos.create_moderation_event_dto \
    import CreateModerationEventDTO
from api.models.moderation_event import ModerationEvent
from api.constants import APIV1LocationContributionErrorMessages
from api.services.submission_quality_service import SubmissionQualityService
from countries.lib.countries import COUNTRY_NAMES

logger = logging.getLogger(__name__)

# Maps each verdict returned by SubmissionQualityService to the warning
# shown to the contributor when it's flagged. To add another AI-judgable
# check, add a field to the tool schema in SubmissionQualityService, add
# the corresponding entry here, and read the field off the verdicts object
# below - no other part of this processor changes.
_WARNING_TITLES = {
    'name_quality': 'Name May Not Look Like a Facility Name',
    'address_quality': 'Address May Not Look Like a Facility Address',
    'address_country_mismatch': 'Address May Not Match Selected Country',
    'multiple_locations': 'Submission May Describe Multiple Locations',
}


class SubmissionQualityProcessor(ContributionProcessor):
    '''
    Flags a new SLC location submission for optional, overridable
    data-quality warnings (implausible name, implausible or
    under-specified address, address/country mismatch, or a submission
    that appears to bundle more than one location) using a single
    Bedrock-hosted LLM call. Unlike DuplicateSubmissionProcessor this
    check is purely advisory: a flagged submission isn't persisted as a
    ModerationEvent until the contributor resubmits with
    ignore_warnings=true, at which point this check is skipped entirely
    rather than re-run, since the contributor has already seen and
    dismissed the warnings.
    '''

    def __init__(self, quality_service: SubmissionQualityService = None):
        self._quality_service = quality_service or SubmissionQualityService()

    def process(
            self,
            event_dto: CreateModerationEventDTO) -> CreateModerationEventDTO:
        if event_dto.request_type != ModerationEvent.RequestType.CREATE.value:
            return super().process(event_dto)

        if event_dto.source != ModerationEvent.Source.SLC.value:
            return super().process(event_dto)

        if event_dto.ignore_warnings:
            logger.info(
                'Submission quality check bypassed via ignore_warnings: '
                'contributor=%s',
                event_dto.contributor.id,
            )
            return super().process(event_dto)

        warnings = self.__collect_warnings(event_dto)
        if warnings:
            logger.info(
                'Submission quality warnings raised: contributor=%s '
                'types=%s',
                event_dto.contributor.id,
                [warning['type'] for warning in warnings],
            )
            event_dto.warnings = warnings
            event_dto.errors = {
                'detail': (
                    APIV1LocationContributionErrorMessages
                    .SUBMISSION_QUALITY_WARNING
                ),
                'warnings': warnings,
            }
            event_dto.status_code = status.HTTP_409_CONFLICT

            return event_dto

        return super().process(event_dto)

    def __collect_warnings(
            self, event_dto: CreateModerationEventDTO) -> list:
        cleaned_data = event_dto.cleaned_data
        name = cleaned_data.get('clean_name', '')
        address = cleaned_data.get('clean_address', '')
        country_code = cleaned_data.get('country_code')
        country_name = COUNTRY_NAMES.get(country_code, country_code or '')

        verdicts = self._quality_service.evaluate(
            name=name, address=address, country_name=country_name
        )
        if verdicts is None:
            return []

        warnings = []
        for warning_type, title in _WARNING_TITLES.items():
            verdict = getattr(verdicts, warning_type)
            if verdict.flagged:
                warnings.append({
                    'type': warning_type,
                    'title': title,
                    'message': verdict.reason,
                })

        return warnings

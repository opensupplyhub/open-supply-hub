import re
from datetime import timedelta
from difflib import SequenceMatcher

from django.utils import timezone
from rest_framework import status

from api.moderation_event_actions.creation.location_contribution \
    .processors.contribution_processor import ContributionProcessor
from api.moderation_event_actions.creation.dtos.create_moderation_event_dto \
    import CreateModerationEventDTO
from api.models.moderation_event import ModerationEvent
from api.constants import APIV1LocationContributionErrorMessages

# How far back to look for a recent submission by the same contributor.
# Sized to cover the worst-case lag before a contributor's own new location
# becomes visible via the pre-submission search: up to 15 minutes for the
# auto-approval automation to pick up the pending moderation event, plus up
# to another 15 minutes for the Logstash pipeline to reindex the approved
# facility into the production-locations OpenSearch index.
DUPLICATE_CHECK_WINDOW_MINUTES = 30

# Both name and address must be at least this similar (SequenceMatcher ratio,
# 0-1) for two submissions to be considered the same location. Country must
# match exactly. Requiring all three keeps this conservative, since a
# single-field fuzzy match (e.g. name only) has previously produced false
# positives elsewhere in this codebase (see ContributorManager.filter_by_name).
NAME_SIMILARITY_THRESHOLD = 0.9
ADDRESS_SIMILARITY_THRESHOLD = 0.9

# Matches any numeric token in a cleaned name or address, e.g. "990" and
# "19123" in "990 spring garden st. philadelphia pa 19123", or "2" in "blue
# horizon facility unit 2". A distinguishing number (street number, suite/
# unit/building number, zip code) can appear anywhere in either field, not
# just at the start, so this isn't anchored to a fixed position.
NUMBER_TOKEN_PATTERN = re.compile(r'\d+')


class DuplicateSubmissionProcessor(ContributionProcessor):
    '''
    Flags a new SLC location submission as a possible duplicate when the
    same contributor submitted a very similar name/address/country within
    the last few minutes. Queries ModerationEvent directly (not the
    OpenSearch production-locations index), since the index may not have
    caught up yet with the contributor's own just-created submission.
    Rejected submissions are excluded, since a rejected event won't become
    a real facility and resubmitting after a rejection is legitimate.
    '''

    def process(
            self,
            event_dto: CreateModerationEventDTO) -> CreateModerationEventDTO:
        if event_dto.request_type != ModerationEvent.RequestType.CREATE.value:
            return super().process(event_dto)

        if event_dto.source != ModerationEvent.Source.SLC.value:
            return super().process(event_dto)

        if event_dto.duplicate_override:
            return super().process(event_dto)

        duplicate = self.__find_recent_duplicate(event_dto)
        if duplicate is not None:
            event_dto.errors = {
                'detail': (
                    APIV1LocationContributionErrorMessages
                    .POSSIBLE_DUPLICATE_SUBMISSION
                ),
                'duplicate_of': {
                    'moderation_id': str(duplicate.uuid),
                    'created_at': duplicate.created_at,
                    'name': duplicate.cleaned_data.get('name'),
                    'address': duplicate.cleaned_data.get('address'),
                    'country': duplicate.cleaned_data.get('country_code'),
                    'duplicate_check_window_minutes':
                        DUPLICATE_CHECK_WINDOW_MINUTES,
                }
            }
            event_dto.status_code = status.HTTP_409_CONFLICT

            return event_dto

        return super().process(event_dto)

    @staticmethod
    def __find_recent_duplicate(event_dto: CreateModerationEventDTO):
        cutoff = timezone.now() - timedelta(
            minutes=DUPLICATE_CHECK_WINDOW_MINUTES
        )
        recent_events = ModerationEvent.objects.filter(
            contributor=event_dto.contributor,
            source=ModerationEvent.Source.SLC.value,
            request_type=ModerationEvent.RequestType.CREATE.value,
            created_at__gte=cutoff,
        ).exclude(status=ModerationEvent.Status.REJECTED.value)

        new_country = event_dto.cleaned_data.get('country_code')
        new_name = event_dto.cleaned_data.get('clean_name', '')
        new_address = event_dto.cleaned_data.get('clean_address', '')

        for candidate in recent_events:
            if candidate.cleaned_data.get('country_code') != new_country:
                continue

            candidate_name = candidate.cleaned_data.get('clean_name', '')
            if DuplicateSubmissionProcessor.__numbers_differ(
                new_name, candidate_name
            ):
                continue

            name_similarity = SequenceMatcher(
                None, new_name, candidate_name
            ).ratio()
            if name_similarity < NAME_SIMILARITY_THRESHOLD:
                continue

            candidate_address = candidate.cleaned_data.get(
                'clean_address', ''
            )
            if DuplicateSubmissionProcessor.__numbers_differ(
                new_address, candidate_address
            ):
                continue

            address_similarity = SequenceMatcher(
                None, new_address, candidate_address
            ).ratio()
            if address_similarity < ADDRESS_SIMILARITY_THRESHOLD:
                continue

            return candidate

        return None

    @staticmethod
    def __numbers_differ(value: str, other_value: str) -> bool:
        '''
        A single-digit change in a distinguishing number (a street number, a
        suite/unit/building number, a zip code) barely moves the overall
        SequenceMatcher ratio, so an otherwise near-identical name or address
        for a genuinely different location (the building next door, a
        different suite in the same building, a different unit sharing a
        base name) could still clear the similarity threshold. Comparing all
        numeric tokens found anywhere in the value (order-sensitive, since
        these numbers aren't anchored to one position), and requiring an
        exact match when both values contain at least one, catches that
        case. Values without any numbers fall back to the overall similarity
        ratio only.
        '''
        numbers = NUMBER_TOKEN_PATTERN.findall(value)
        other_numbers = NUMBER_TOKEN_PATTERN.findall(other_value)
        if not numbers or not other_numbers:
            return False

        return numbers != other_numbers

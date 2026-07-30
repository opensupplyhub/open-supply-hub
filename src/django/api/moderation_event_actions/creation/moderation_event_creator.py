from django.db import connection, transaction

from api.moderation_event_actions.creation.event_creation_strategy import (
    EventCreationStrategy
)
from api.moderation_event_actions.creation.dtos.create_moderation_event_dto \
    import CreateModerationEventDTO
from api.moderation_event_actions.creation.location_contribution \
    import duplicate_check
from api.models.moderation_event import ModerationEvent

# Namespace for pg_advisory_xact_lock so the duplicate-check lock can't
# collide with any other advisory lock usage. Arbitrary but must stay
# unique within the application.
DUPLICATE_LOCK_NAMESPACE = 2980


class ModerationEventCreator:
    def __init__(self, strategy: EventCreationStrategy) -> None:
        self.__strategy = strategy

    def perform_event_creation(
            self,
            event_dto: CreateModerationEventDTO
            ) -> CreateModerationEventDTO:
        processed_event = self.__strategy.serialize(event_dto)

        if processed_event.errors:
            return event_dto

        if duplicate_check.applies_to(processed_event):
            return self.__create_serialized_per_contributor(
                event_dto, processed_event
            )

        event_dto.moderation_event = self.__create_event(processed_event)

        return event_dto

    def __create_serialized_per_contributor(
            self,
            event_dto: CreateModerationEventDTO,
            processed_event: CreateModerationEventDTO
            ) -> CreateModerationEventDTO:
        '''
        Close the duplicate-check race: two concurrent identical requests
        can both pass DuplicateSubmissionProcessor's early check, because
        neither moderation event exists yet when the other one looks. The
        per-contributor pg_advisory_xact_lock serializes the authoritative
        re-check and the insert, so the second request's re-check sees the
        first request's committed row and returns 409. The lock is held
        only for this query + insert (no external calls) and is released
        automatically at transaction end.
        '''
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute(
                    'SELECT pg_advisory_xact_lock(%s, %s)',
                    [DUPLICATE_LOCK_NAMESPACE, processed_event.contributor.id],
                )

            duplicate = duplicate_check.find_recent_duplicate(processed_event)
            if duplicate is not None:
                duplicate_check.set_duplicate_error(
                    processed_event, duplicate
                )
                return event_dto

            event_dto.moderation_event = self.__create_event(processed_event)

        return event_dto

    @staticmethod
    def __create_event(
            processed_event: CreateModerationEventDTO) -> ModerationEvent:
        return ModerationEvent.objects.create(
            contributor=processed_event.contributor,
            request_type=processed_event.request_type,
            raw_data=processed_event.raw_data,
            cleaned_data=processed_event.cleaned_data,
            geocode_result=processed_event.geocode_result,
            source=processed_event.source,
            os=processed_event.os,
            backfilled_fields=processed_event.backfilled_fields,
        )

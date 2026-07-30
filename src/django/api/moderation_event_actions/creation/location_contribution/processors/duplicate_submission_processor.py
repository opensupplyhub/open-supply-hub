from api.moderation_event_actions.creation.location_contribution \
    .processors.contribution_processor import ContributionProcessor
from api.moderation_event_actions.creation.dtos.create_moderation_event_dto \
    import CreateModerationEventDTO
from api.moderation_event_actions.creation.location_contribution \
    import duplicate_check


class DuplicateSubmissionProcessor(ContributionProcessor):
    '''
    Flags a new SLC location submission as a possible duplicate when the
    same contributor submitted a very similar name/address/country within
    the last few minutes. Queries ModerationEvent directly (not the
    OpenSearch production-locations index), since the index may not have
    caught up yet with the contributor's own just-created submission.

    This check is advisory only: it runs early so a duplicate fails fast,
    before the geocoding call, but two concurrent identical requests can
    both pass it. The authoritative re-check runs in
    ModerationEventCreator under a per-contributor advisory lock — do not
    remove either call site without the other.
    '''

    def process(
            self,
            event_dto: CreateModerationEventDTO) -> CreateModerationEventDTO:
        if not duplicate_check.applies_to(event_dto):
            return super().process(event_dto)

        duplicate = duplicate_check.find_recent_duplicate(event_dto)
        if duplicate is not None:
            duplicate_check.set_duplicate_error(event_dto, duplicate)

            return event_dto

        return super().process(event_dto)

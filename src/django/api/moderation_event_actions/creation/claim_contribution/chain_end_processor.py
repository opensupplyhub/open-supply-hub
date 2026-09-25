from api.moderation_event_actions.creation.dtos.create_moderation_event_dto \
    import CreateModerationEventDTO
from api.moderation_event_actions.creation.location_contribution \
    .processors.contribution_processor import ContributionProcessor


class ChainEndProcessor(ContributionProcessor):
    '''
    Terminates a processor chain. ContributionProcessor treats reaching
    the end of the chain as an internal error (the SLC chain ends in a
    processor that never delegates), so a chain built from shared
    processors that all delegate onward needs an explicit terminal.
    '''

    def process(
            self,
            event_dto: CreateModerationEventDTO) -> CreateModerationEventDTO:
        return event_dto

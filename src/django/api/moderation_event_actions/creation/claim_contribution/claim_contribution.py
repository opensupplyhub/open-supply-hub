from api.moderation_event_actions.creation.claim_contribution \
    .chain_end_processor import ChainEndProcessor
from api.moderation_event_actions.creation.dtos.create_moderation_event_dto \
    import CreateModerationEventDTO
from api.moderation_event_actions.creation.event_creation_strategy \
    import EventCreationStrategy
from api.moderation_event_actions.creation.location_contribution \
    .processors.production_location_data_processor \
    import ProductionLocationDataProcessor


class ClaimContribution(EventCreationStrategy):
    '''
    Builds the cleaned_data for a CLAIM moderation event: the name and
    address an approved claimant asserted for their production location,
    recorded as a contribution so it appears in the location's
    submission history.

    Only ProductionLocationDataProcessor runs. The rest of the SLC chain
    does not apply here: a claim carries no partner fields (permission
    and partner-field-type checks), CLAIM events have no source type
    (source check), the duplicate and quality checks are scoped to SLC
    submissions by design and, if wanted for claims, belong at claim
    submission time rather than at approval, and the location is decided
    by the claim contribution service, which passes coordinates in
    raw_data so the geocoding processor would be a no-op.
    '''

    def serialize(
            self,
            event_dto: CreateModerationEventDTO) -> CreateModerationEventDTO:
        data_processor = ProductionLocationDataProcessor()
        data_processor.set_next(ChainEndProcessor())
        return data_processor.process(event_dto)

from api.moderation_event_actions.creation.event_creation_strategy \
    import EventCreationStrategy
from api.moderation_event_actions.creation.location_contribution \
    .processors.contribution_processor import ContributionProcessor
from api.moderation_event_actions.creation.location_contribution \
    .processors.source_processor import SourceProcessor
from api.moderation_event_actions.creation.location_contribution \
    .processors.production_location_data_processor \
    import ProductionLocationDataProcessor
from api.moderation_event_actions.creation.location_contribution \
    .processors.geocoding_processor import GeocodingProcessor
from api.moderation_event_actions.creation.dtos.create_moderation_event_dto \
    import CreateModerationEventDTO


class LocationContribution(EventCreationStrategy):
    '''
    The class-based algorithm that validates, extracts, and geocodes the
    retrieved location data from the user before saving it as
    a moderation event.
    '''

    def serialize(
            self,
            event_dto: CreateModerationEventDTO) -> CreateModerationEventDTO:
        entry_location_data_processor = self.__setup_location_data_processors()

        processed_location_data = entry_location_data_processor.process(
            event_dto
        )

        return processed_location_data

    @staticmethod
    def __setup_location_data_processors() -> ContributionProcessor:
        location_data_processors = (
            SourceProcessor(),
            ProductionLocationDataProcessor(),
            GeocodingProcessor()
        )
        # Link each processor to the next one.
        for current_processor, next_processor in zip(
                location_data_processors, location_data_processors[1:]):
            current_processor.set_next(next_processor)

        return location_data_processors[0]

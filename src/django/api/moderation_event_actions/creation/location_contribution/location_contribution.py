from api.moderation_event_actions.creation.event_creation_strategy \
    import EventCreationStrategy
from api.moderation_event_actions.creation.location_contribution \
    .processors.contribution_processor import ContributionProcessor
from api.moderation_event_actions.creation.location_contribution \
    .processors.source_processor import SourceProcessor


class LocationContribution(EventCreationStrategy):
    '''
    The class-based algorithm that validates, extracts, and geocodes the
    retrieved location data from the user before saving it as
    a moderation event.
    '''

    def serialize(self, moderation_event_data):
        entry_location_data_processor = self.__setup_location_data_processors()
        processed_location_data = entry_location_data_processor.handle(
            moderation_event_data
        )

        return processed_location_data

    @classmethod
    def __setup_location_data_processors(cls) -> ContributionProcessor:
        location_data_processors = (
            SourceProcessor(),
        )
        for index in range(len(location_data_processors) - 1):
            location_data_processors[index].set_next(
                location_data_processors[index + 1]
            )

        entry_location_data_processor = location_data_processors[0]

        return entry_location_data_processor

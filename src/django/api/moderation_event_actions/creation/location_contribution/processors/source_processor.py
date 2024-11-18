from api.moderation_event_actions.creation.location_contribution \
    .processors.contribution_processor import ContributionProcessor


class SourceProcessor(ContributionProcessor):

    def handle(self, event):
        print('HI. I am SourceProcessor')
        return event

        # return super().handle(event)
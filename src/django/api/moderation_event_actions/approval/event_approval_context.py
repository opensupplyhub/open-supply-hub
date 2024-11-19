from api.moderation_event_actions.approval.event_approval_strategy import (
    EventApprovalStrategy,
)


class EventApprovalContext:
    '''
    Class defines which interface execute for the processing of a moderation event.
    '''

    def __init__(self, strategy: EventApprovalStrategy) -> None:
        self.__strategy = strategy

    def run_processing(self) -> None:
        result = self.__strategy.process_moderation_event()

        return result

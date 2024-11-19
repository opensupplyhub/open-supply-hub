from abc import ABC, abstractmethod


class EventApprovalStrategy(ABC):
    '''
    Abstract class for approval moderation event strategies.
    '''

    @abstractmethod
    def process_moderation_event(self) -> None:
        pass

from abc import ABC, abstractmethod

from api.models.facility.facility_list_item import FacilityListItem


class EventApprovalStrategy(ABC):
    '''
    Abstract class for approval moderation event strategies.
    '''

    @abstractmethod
    def process_moderation_event(self) -> FacilityListItem:
        pass

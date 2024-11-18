from abc import ABC, abstractmethod
from typing import List, Dict


class EventCreationStrategy(ABC):
    @abstractmethod
    def serialize(self, moderation_event_data) -> List[Dict]:
        pass

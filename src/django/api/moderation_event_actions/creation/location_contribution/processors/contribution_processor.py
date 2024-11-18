from __future__ import annotations
from abc import ABC, abstractmethod


class ContributionProcessor(ABC):
    '''
    The class that defines the common interface for location contribution
    processors. Essentially, it is used to implement the Chain of
    Responsibility pattern, allowing the graceful stopping of data processing
    in case an error occurs, or allowing the entire chain of processors to run
    through in case of a successful pass.
    '''

    _next: ContributionProcessor = None

    def set_next(self, next: ContributionProcessor):
        self._next = next

    @abstractmethod
    def handle(self, event) -> None:
        if self._next:
            return self._next.handle(event)

        return None

from abc import ABC, abstractmethod


class EarlyValidator(ABC):

    @abstractmethod
    def validate(self, row: dict) -> dict:
        pass
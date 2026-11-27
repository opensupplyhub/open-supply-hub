from abc import ABC, abstractmethod


class RowSerializer(ABC):
    # CompositeRowSerializer hands each serializer the row after its
    # cleanup (comma spacing, quote removal, etc.). A serializer that must
    # judge the values exactly as the contributor sent them, such as a
    # length limit, sets this to True to receive the original row instead.
    validates_raw_row = False

    @abstractmethod
    def validate(self, row: dict) -> dict:
        pass

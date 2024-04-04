from typing import List
from contricleaner.lib.dto.list_dto import ListDTO
from contricleaner.lib.handlers.list_row_handler import ListRowHandler
from contricleaner.lib.validators.pre_validators.pre_header_validator import PreHeaderValidator
from contricleaner.lib.validators.pre_validators.composite_pre_validator import CompositePreValidator


class PreValidationHandler(ListRowHandler):
    __next: ListRowHandler

    def setNext(self, next: ListRowHandler):
        self.__next = next

    def handle(self, rows: List[dict]) -> ListDTO:
        composite_early_validator = CompositePreValidator()
        composite_early_validator.add_validator(PreHeaderValidator())

        result = composite_early_validator.validate(rows)

        if len(result["errors"]) > 0:
            return ListDTO([], result["errors"])

        try:
            return self.__next.handle(rows)
        except Exception:
            raise Exception("Next Handler wasn't set")

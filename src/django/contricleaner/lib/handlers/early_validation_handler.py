from typing import List
from contricleaner.lib.dto.list_dto import ListDTO
from contricleaner.lib.validators.early_validators.early_header_validator import EarlyHeaderValidator
from contricleaner.lib.validators.early_validators.composite_early_validator import CompositeEarlyValidator


class EarlyValidationHandler:

    def setNext(self, next):
        self.__next = next

    def handle(self, rows: List[dict]) -> ListDTO:
        composite_early_validator = CompositeEarlyValidator()
        composite_early_validator.add_validator(EarlyHeaderValidator())

        result = composite_early_validator.validate(rows)

        if len(result["errors"]) > 0:
            return ListDTO([],result["errors"])
        
        return self.__next.handle(rows)
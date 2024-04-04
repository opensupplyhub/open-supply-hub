from typing import List
from contricleaner.lib.validators.\
    early_validators.early_validator import EarlyValidator


class CompositeEarlyValidator(EarlyValidator):
    __validators: List[EarlyValidator] = []

    def add_validator(self, validator: EarlyValidator):
        self.__validators.append(validator)

    def validate(self, rows: List[dict]) -> dict:
        validation = {
            "errors": [],
        }
        for validator in self.__validators:
            result = validator.validate(rows)
            if len(result.keys()) > 0:
                validation["errors"].append(result)
        return validation

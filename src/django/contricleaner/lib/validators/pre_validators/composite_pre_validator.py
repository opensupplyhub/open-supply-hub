from typing import List

from contricleaner.lib.validators.pre_validators \
    .pre_validator import PreValidator


class CompositePreValidator(PreValidator):
    def __init__(self) -> None:
        self.__validators: List[PreValidator] = []

    def add_validator(self, validator: PreValidator):
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

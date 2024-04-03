from typing import List
from contricleaner.lib.validators.\
    early_validators.early_validator import EarlyValidator


class EarlyHeaderValidator(EarlyValidator):
    __required_fields = {"name",
                       "address",
                       "country"}

    def validate(self, rows: List[dict]) -> dict:
        for row in rows:
            raw_row = row
            diff = self.__required_fields.difference(raw_row.keys())

            if len(diff) == 0:
                return {}


        return {
            "message": "Required Fields are missing: {}".format(', '.join(self.__required_fields)),
            "type": "Error",
        }
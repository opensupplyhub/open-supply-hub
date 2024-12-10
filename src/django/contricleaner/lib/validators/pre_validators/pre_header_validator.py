from typing import List

from contricleaner.lib.validators.pre_validators \
    .pre_validator import PreValidator
from contricleaner.constants import NON_FIELD_ERRORS_KEY


class PreHeaderValidator(PreValidator):
    __required_fields = {'name',
                         'address',
                         'country'}

    def validate(self, rows: List[dict]) -> dict:
        for row in rows:
            raw_row = row
            diff = self.__required_fields.difference(raw_row.keys())

            if len(diff) == 0:
                return {}

        return {
            'message': 'Required Fields are missing: {}.'
            .format(', '.join(self.__required_fields)),
            'field': NON_FIELD_ERRORS_KEY,
            'type': 'RequiredFieldsMissingError',
        }

from typing import List, Dict

from contricleaner.lib.dto.list_dto import ListDTO
from contricleaner.lib.handlers.list_row_handler import ListRowHandler
from contricleaner.lib.validators.pre_validators \
    .pre_header_validator import PreHeaderValidator
from contricleaner.lib.validators.pre_validators \
    .composite_pre_validator import CompositePreValidator


class PreValidationHandler(ListRowHandler):

    def handle(self, rows: List[Dict]) -> ListDTO:
        composite_pre_validator = CompositePreValidator()
        composite_pre_validator.add_validator(PreHeaderValidator())

        result = composite_pre_validator.validate(rows)

        if len(result['errors']) > 0:
            return ListDTO(errors=result['errors'])

        return super().handle(rows)

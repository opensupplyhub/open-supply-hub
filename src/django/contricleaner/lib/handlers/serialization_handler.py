from typing import List

from contricleaner.lib.dto.list_dto import ListDTO
from contricleaner.lib.handlers.list_row_handler import ListRowHandler


class SerializationHandler(ListRowHandler):

    def handle(self, rows: List[dict]) -> ListDTO:
        # composite_early_validator = CompositePreValidator()
        # composite_early_validator.add_validator(PreHeaderValidator())

        result = composite_early_validator.validate(rows)
        if len(result['errors']) > 0:
            row =  RowDTO(
            raw_json=raw_row,
            name=dict_res.get("name", ""),
            clean_name=dict_res.get("clean_name", ""),
            address=dict_res.get("address", ""),
            clean_address=dict_res.get("clean_address", ""),
            country_code=dict_res.get("country_code", ""),
            sector=dict_res.get("sector", []),
            fields=dict_res.get("fields", {}),
            errors=dict_res.get("errors", []),
        )
            return ListDTO(rows=rows)

        try:
            return self._next.handle(rows)
        except Exception:
            raise Exception("Next Handler wasn't set.")

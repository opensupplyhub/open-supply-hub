from typing import List

from contricleaner.lib.dto.header_dto import HeaderDTO
from .header_required_serializer import HeaderRequiredSerializer


class HeaderCompositeSerializer:
    def __init__(self):
        self.validators = [
            HeaderRequiredSerializer()
        ]

    def get_validated_headers(self, headers: List[str]):

        res = {
            "headers": headers,
            "errors": [],
        }

        for validator in self.validators:
            res = validator.validate(headers, res)

        return HeaderDTO(
            headers=res.get("headers", ""),
            errors=res.get("errors", "")
        )

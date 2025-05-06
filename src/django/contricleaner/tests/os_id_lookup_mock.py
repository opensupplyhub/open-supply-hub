from contricleaner.lib.client_abstractions.lookup_interface import (
    LookUpInterface
)


class OSIDLookUpMock(LookUpInterface):
    def __init__(self) -> None:
        super().__init__(lookup_field="id")

    def get(self, key: str) -> dict:
        return {key: key}

    def bulk_get(self, keys: list) -> dict:
        self.map = {
            'YX1234567ABCD8E': None
        }

        for key in keys:
            self.map[key] = key

        return self.map

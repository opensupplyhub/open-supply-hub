from api.models import Facility
from contricleaner.lib.client_abstractions.lookup_interface import (
    LookUpInterface
)


class OSIDLookUp(LookUpInterface):

    def __init__(self) -> None:
        super().__init__(lookup_field="id")

    def get(self, key: str) -> dict:
        lookup = {f"{self.lookup_field}__iexact": key}
        try:
            facility = Facility.objects.get(**lookup)
            return {key: facility.id}
        except Facility.DoesNotExist:
            return {key: None}

    def bulk_get(self, keys: list) -> dict:
        map = {}
        filter_field = f"{self.lookup_field}__in"
        facilities = Facility.objects.filter(**{filter_field: keys})
        ids_list = [facility.id for facility in facilities]
        for key in keys:
            map[key] = key if key in ids_list else None
        return map

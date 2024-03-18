from .row_serializer import RowSerializer


class RowEmptySerializer(RowSerializer):
    def validate(self, row: dict, current: dict) -> dict:
        keys = set(row.keys()).difference(current.keys())
        for key in keys:
            current[key] = row[key]

        return current

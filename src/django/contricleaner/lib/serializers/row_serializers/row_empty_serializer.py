from .row_serializer import RowSerializer


class RowEmptySerializer(RowSerializer):
    def validate(self, row: dict, current: dict) -> dict:
        excluded_keys = ['additional_ids']
        keys = (
            set(row.keys())
            .difference(current.keys())
            .difference(excluded_keys)
        )
        for key in keys:
            current[key] = row[key]

        return current

from contricleaner.lib.serializers.row_serializers.row_serializer import (
    RowSerializer,
)


class RowAdditionalIdsSerializer(RowSerializer):
    def validate(self, row: dict, current: dict) -> dict:
        additional_ids = row.get('additional_ids', {})
        if isinstance(additional_ids, dict):
            for key, value in additional_ids.items():
                current[key] = value

        return current

from .row_serializer import RowSerializer


class RowCleanedUserDataSerializer(RowSerializer):
    def validate(self, row: dict, current: dict) -> dict:
        current["cleaned_user_data"] = row.copy()
        return current

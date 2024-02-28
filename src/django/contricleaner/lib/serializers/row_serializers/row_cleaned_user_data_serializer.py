class RowCleanedUserDataSerializer:
    def validate(self, row: dict, current: dict) -> dict:
        current["cleaned_user_data"] = row.copy()
        return current

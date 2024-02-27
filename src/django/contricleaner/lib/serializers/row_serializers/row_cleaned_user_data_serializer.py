class RowCleanedUserDataSerializer:
    '''
    This class is responsible for cleaning the user data and adding it to the row
    '''

    def validate(self, row: dict, current: dict) -> dict:
        current["cleaned_user_data"] = row.copy()
        return current

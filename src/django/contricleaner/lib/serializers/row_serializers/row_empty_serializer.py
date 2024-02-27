class RowEmptySerializer:
    '''
    This class is used to validate the row and add the missing fields to the row.
    '''

    def validate(self, row: dict, current: dict) -> dict:
        keys = set(row.keys()).difference(current.keys())
        for key in keys:
            current[key] = row[key]

        return current

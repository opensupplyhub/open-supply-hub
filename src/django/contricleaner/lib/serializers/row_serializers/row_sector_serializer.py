class RowSectorSerializer:
    '''
    This class is used to validate the sector field of a row.
    '''

    def validate(self, row: dict, current: dict) -> dict:
        current["sector"] = row["sector"].split(",")

        return current

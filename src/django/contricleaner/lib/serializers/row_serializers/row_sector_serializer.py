class RowSectorSerializer:
    def validate(self, row: dict, current: dict) -> dict:
        current["sector"] = row["sector"].split(",")

        return current

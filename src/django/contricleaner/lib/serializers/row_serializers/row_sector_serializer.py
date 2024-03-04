from .row_serializer import RowSerializer


class RowSectorSerializer(RowSerializer):
    def validate(self, row: dict, current: dict) -> dict:
        current["sector"] = row["sector"].split(",")

        return current

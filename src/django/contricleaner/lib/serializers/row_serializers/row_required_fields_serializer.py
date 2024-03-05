from .row_serializer import RowSerializer


class RowRequiredFieldsSerializer(RowSerializer):
    required_fields = {"name",
                       "address",
                       "country"}

    def validate(self, row: dict, current: dict) -> dict:
        diff = self.required_fields.difference(row.keys())

        if len(diff) > 0:
            current["errors"].append(
                {
                    "message": "{} are missing".format(', '.join(diff)),
                    "type": "Error",
                }
            )

        return current

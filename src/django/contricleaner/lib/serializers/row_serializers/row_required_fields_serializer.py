from .row_serializer import RowSerializer


class RowRequiredFieldsSerializer(RowSerializer):

    def validate(self, row: dict, current: dict) -> dict:
        required_fields = ["name",
                           "address",
                           "country"]

        for required_field in required_fields:
            if required_field not in row.keys():
                current["errors"].append(
                    {
                        "message": "Missed field {}".format(required_field),
                        "type": "Error",
                    }
                )

        return current

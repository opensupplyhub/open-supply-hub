from typing import List

from .header_serializer import HeaderSerializer


class HeaderRequiredSerializer(HeaderSerializer):

    def validate(self, headers: List[str], current: dict) -> dict:
        required_fields = ["name",
                           "address",
                           "country"]

        for required_field in required_fields:
            if required_field in headers:
                pass
            else:
                current["errors"].append(
                    {
                        "message": "Missed required field '{}'"
                            .format(required_field),
                        "type": "Error",
                    }
                )

        return current

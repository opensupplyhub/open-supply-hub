from countries.lib.get_country_code import get_country_code
from .row_serializer import RowSerializer


class RowCountrySerializer(RowSerializer):
    def validate(self, row: dict, current: dict) -> dict:
        country = row.get("country", '')

        try:
            current["country_code"] = get_country_code(country)
            return current
        except ValueError as exc:
            current["errors"].append(
                {
                    "message": str(exc),
                    "type": "Error",
                }
            )
            return current

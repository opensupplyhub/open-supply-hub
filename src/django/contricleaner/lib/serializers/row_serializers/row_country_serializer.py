from countries.lib.get_country_code import get_country_code


class RowCountrySerializer:
    '''
    This class is responsible for validating the country field in the row.
    '''

    def validate(self, row: dict, current: dict) -> dict:
        try:
            current["country_code"] = get_country_code(row["country"])
            return current
        except ValueError as exc:
            current["errors"].append(
                {
                    "message": str(exc),
                    "type": "Error",
                }
            )
            return current

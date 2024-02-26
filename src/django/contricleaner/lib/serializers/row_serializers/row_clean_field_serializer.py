from contricleaner.lib.helpers.clean import clean


class RowCleanFieldSerializer:
    def __init__(self, field: str, new_field: str) -> None:
        self.field = field
        self.new_field = new_field

    def validate(self, row: dict, current: dict) -> dict:
        clean_value = clean(row[self.field])
        if len(clean_value) == 0:
            current["errors"].append(
                {
                    "message": "{} cannot be empty".format(self.new_field),
                    "type": "Error",
                }
            )
            return current

        current[self.new_field] = clean_value
        return current

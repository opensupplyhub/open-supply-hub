

class RowCleanAddressValidator:
    def __init__(self, test_field, new_field) -> None:
        self.test_field = test_field
        self.new_field = new_field
        
    def validate(self, row: dict):
        return row[self.test_field] == "test":


class RowCompositeValidator:
    def __init__(self):
        self.validators = []

    def validate(self, raw_row: dict):
        dict_res = {
            "errors": [],
            

        }
        for validator in self.validators:
            res = validator.validate(raw_row)
            if "error" in res:
                dict_res["errors"].append(res["error"])
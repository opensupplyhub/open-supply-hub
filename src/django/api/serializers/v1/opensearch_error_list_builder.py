class OpenSearchErrorListBuilder:
    def __init__(self, validators):
        self.validators = validators

    def build_error_list(self, data):
        errors = []
        for validator in self.validators:
            errors.extend(validator.validate(data))
        return errors

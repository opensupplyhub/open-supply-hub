class OpenSearchErrorListBuilder:
    def __init__(self, validators):
        self.validators = validators

    def build_error_list(self, data):
        errors = []
        for validator in self.validators:
            validator.validate(data, errors)
        return errors

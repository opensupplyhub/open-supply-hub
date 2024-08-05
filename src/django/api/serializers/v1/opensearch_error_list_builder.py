class OpenSearchErrorListBuilder:
    def __init__(self, validators):
        self.validators = validators

    def build_error_list(self, data):
        errors = []
        for validator in self.validators:
            validator_errors = validator.validate(data)
            if validator_errors:
                errors.extend(validator_errors)
        return errors

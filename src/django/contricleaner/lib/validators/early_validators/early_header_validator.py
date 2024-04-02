from contricleaner.lib.validators.\
    early_validators.early_validator import EarlyValidator


class EarlyHeaderValidator(EarlyValidator):

    def validate(self, row: dict) -> dict:
        return row
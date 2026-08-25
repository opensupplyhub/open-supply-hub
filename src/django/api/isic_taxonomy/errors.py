from dataclasses import dataclass


@dataclass(frozen=True)
class IsicTaxonomyError:
    message: str
    row: int | None = None
    column: str | None = None

    def format(self) -> str:
        if self.row is not None and self.column is not None:
            return f'Row {self.row}, column "{self.column}": {self.message}'
        if self.row is not None:
            return f'Row {self.row}: {self.message}'
        return self.message


class IsicTaxonomyValidationError(Exception):
    '''Raised when spreadsheet validation fails before publish.'''

    def __init__(self, errors: list[IsicTaxonomyError]):
        self.errors = errors
        messages = [error.format() for error in errors]
        super().__init__('\n'.join(messages))


class IsicTaxonomyPublishError(Exception):
    '''Raised when S3 upload or DB promotion fails during publish.'''

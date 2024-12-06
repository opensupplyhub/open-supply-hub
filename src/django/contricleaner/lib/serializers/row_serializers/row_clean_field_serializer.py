from contricleaner.lib.helpers.clean import clean
from contricleaner.lib.serializers.row_serializers.row_serializer \
    import RowSerializer


class RowCleanFieldSerializer(RowSerializer):
    def __init__(self, field: str, new_field: str) -> None:
        self.field = field
        self.new_field = new_field

    def validate(self, row: dict, current: dict) -> dict:
        clean_value = clean(row.get(self.field, ''))

        if not clean_value:
            current['errors'].append(
                {
                    'message': (
                        '{} cannot consist solely of '
                        'punctuation or whitespace.'
                        ).format(self.field),
                    'field': self.field,
                    'type': 'Error',
                }
            )
            return current

        current[self.new_field] = clean_value
        return current

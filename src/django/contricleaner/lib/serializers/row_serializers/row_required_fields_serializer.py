from typing import List, Set, Dict


from contricleaner.lib.serializers.row_serializers.row_serializer \
    import RowSerializer
from contricleaner.constants import NON_FIELD_ERRORS_KEY


class RowRequiredFieldsSerializer(RowSerializer):
    __required_fields = {
        'name',
        'address',
        'country'
    }
    __valid_field_value_lengths = {'name': 200, 'address': 200}

    def validate(self, row: dict, current: dict) -> dict:
        missing_fields = self.__required_fields.difference(row.keys())

        if len(missing_fields) > 0:
            current['errors'].append(
                {
                    'message': '{} are missing.'.format(
                        ', '.join(missing_fields)),
                    'field': NON_FIELD_ERRORS_KEY,
                    'type': 'Error',
                }
            )

        field_value_length_errors = self.__validate_field_value_lengths(
            missing_fields, row
        )
        current['errors'].extend(field_value_length_errors)

        return current

    def __validate_field_value_lengths(self,
                                       missing_fields: Set[str],
                                       input_row: Dict) -> List[Dict]:
        errors = []

        for field, max_length in self.__valid_field_value_lengths.items():
            if (field not in missing_fields):
                value_len = len(input_row[field])

                if value_len > max_length:
                    errors.append(
                        {
                            'message': ('There is a problem with the {0}: '
                                        'Ensure this value has at most 200 '
                                        'characters. (it has {1})').format(
                                            field, value_len),
                            'field': field,
                            'type': 'ValidationError',
                        }
                    )

        return errors

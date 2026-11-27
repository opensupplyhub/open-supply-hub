from typing import Iterable, List, Set, Dict


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
    # The limits apply to what the contributor submitted, not to the
    # cleaned value: cleanup can add characters (e.g. a space after each
    # comma), which must not push a valid submission over the limit. The
    # name and address columns are wider than these limits to hold that
    # growth (OSDEV-1085).
    validates_raw_row = True

    def __init__(self, skip_length_check_fields: Iterable[str] = ()) -> None:
        # Fields whose value was not submitted by the contributor but copied
        # from what is already stored for the location (e.g. backfilled on a
        # partial update). Stored values are cleaned, so they may exceed the
        # submission limit and are not checked against it.
        self.__skip_length_check_fields = frozenset(skip_length_check_fields)

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
            if (field not in missing_fields
                    and field not in self.__skip_length_check_fields):
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

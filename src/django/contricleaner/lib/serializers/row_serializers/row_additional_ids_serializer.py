import re
from contricleaner.constants import AdditionalIDs
from contricleaner.lib.serializers.row_serializers.row_serializer import (
    RowSerializer,
)


class RowAdditionalIdsSerializer(RowSerializer):
    __DUNS_RE = re.compile(r'^\d{9}$')
    __LEI_RE = re.compile(r'^[A-Z0-9]{18}\d{2}$')

    def validate(self, row: dict, current: dict) -> dict:
        additional_identifiers = row.get('additional_identifiers')

        if additional_identifiers is None:
            return current

        if not isinstance(additional_identifiers, dict):
            current['errors'].append(
                {
                    'message': 'Expected value for additional_identifiers to '
                    f'be a dict but got {additional_identifiers}.',
                    'field': 'additional_identifiers',
                    'type': 'ValueError',
                }
            )

            return current

        for key, value in additional_identifiers.items():
            if key not in AdditionalIDs.ALLOWED_KEYS:
                current['errors'].append(
                    {
                        'message': f'Unexpected key {key} in '
                        'additional_identifiers. The allowed keys are: '
                        f'{", ".join(sorted(AdditionalIDs.ALLOWED_KEYS))}.',
                        'field': 'additional_identifiers',
                        'type': 'KeyError',
                    }
                )
                continue

            if not isinstance(value, str):
                current['errors'].append(
                    {
                        'message': f'Expected value for {key} to be a string '
                        f'but got {type(value).__name__}.',
                        'field': 'additional_identifiers',
                        'type': 'ValueError',
                    }
                )
                continue

            if key == AdditionalIDs.DUNS_ID and not self.__is_valid_duns(
                value
            ):
                current['errors'].append(
                    {
                        'message': f'Invalid `duns_id`: {value}. '
                        'It should be a 9-digit number.',
                        'field': 'additional_identifiers',
                        'type': 'ValueError',
                    }
                )

            elif key == AdditionalIDs.LEI_ID and not self.__is_valid_lei(
                value
            ):
                current['errors'].append(
                    {
                        'message': f'Invalid `lei_id`: {value}. '
                        'It should be a 20-character string '
                        'with 18 alphanumeric characters followed by '
                        '2 digits.',
                        'field': 'additional_identifiers',
                        'type': 'ValueError',
                    }
                )

            elif key == AdditionalIDs.RBA_ID and not self.__is_valid_rba(
                value
            ):
                current['errors'].append(
                    {
                        'message': f'Invalid `rba_id`: {value}. '
                        'It should be a string with a maximum length of 255 '
                        'characters.',
                        'field': 'additional_identifiers',
                        'type': 'ValueError',
                    }
                )

            current[key] = value

        return current

    def __is_valid_duns(self, value: str) -> bool:
        return bool(self.__DUNS_RE.fullmatch(value))

    def __is_valid_lei(self, value: str) -> bool:
        return bool(self.__LEI_RE.fullmatch(value))

    def __is_valid_rba(self, value: str) -> bool:
        return bool(isinstance(value, str) and len(value) <= 255)

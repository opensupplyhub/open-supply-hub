import re
from contricleaner.lib.serializers.row_serializers.row_serializer import (
    RowSerializer,
)


class RowAdditionalIdsSerializer(RowSerializer):
    __DUNS_ID = 'duns_id'
    __LEI_ID = 'lei_id'
    __RBA_ID = 'rba_id'

    __ALLOWED_KEYS = {
        __DUNS_ID,
        __LEI_ID,
        __RBA_ID,
    }

    __DUNS_RE = re.compile(r'^\d{9}$')
    __LEI_RE = re.compile(r'^[A-Z0-9]{18}[0-9]{2}$')

    def validate(self, row: dict, current: dict) -> dict:
        additional_ids = row.get('additional_ids')

        if additional_ids is None:
            return current

        if not isinstance(additional_ids, dict):
            current['errors'].append(
                {
                    'message': 'Expected value for additional_ids to be '
                    f'a dict but got {additional_ids}.',
                    'field': 'additional_ids',
                    'type': 'ValueError',
                }
            )

            return current

        for key, value in additional_ids.items():
            if key not in self.__ALLOWED_KEYS:
                current['errors'].append(
                    {
                        'message': f'Unexpected key {key} in additional_ids. '
                        'The allowed keys are: '
                        f'{", ".join(self.__ALLOWED_KEYS)}.',
                        'field': 'additional_ids',
                        'type': 'KeyError',
                    }
                )
                continue

            if not isinstance(value, str):
                current['errors'].append(
                    {
                        'message': f'Expected value for {key} to be a string '
                        f'but got {type(value).__name__}.',
                        'field': 'additional_ids',
                        'type': 'ValueError',
                    }
                )
                continue

            if key == self.__DUNS_ID and not self.__is_valid_duns(value):
                current['errors'].append(
                    {
                        'message': f'Invalid `duns_id`: {value}. '
                        'It should be a 9-digit number.',
                        'field': 'additional_ids',
                        'type': 'ValueError',
                    }
                )

            elif key == self.__LEI_ID and not self.__is_valid_lei(value):
                current['errors'].append(
                    {
                        'message': f'Invalid `lei_id`: {value}. '
                        'It should be a 20-character string '
                        'with 18 alphanumeric characters followed by '
                        '2 digits.',
                        'field': 'additional_ids',
                        'type': 'ValueError',
                    }
                )

            elif key == self.__RBA_ID and not self.__is_valid_rba(value):
                current['errors'].append(
                    {
                        'message': f'Invalid `rba_id`: {value}. '
                        'It should be a string with a maximum length of 255 '
                        'characters.',
                        'field': 'additional_ids',
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

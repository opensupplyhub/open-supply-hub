import re
from contricleaner.lib.helpers.split_values import split_values
from contricleaner.lib.serializers.row_serializers.row_serializer import (
    RowSerializer,
)


class RowParentCompanyOSIDSerializer(RowSerializer):
    def __init__(self, split_pattern: str) -> None:
        self.split_pattern = split_pattern

    def validate(self, row: dict, current: dict) -> dict:
        field = 'parent_company_os_id'
        value = row.get(field)

        if not value:
            return current
        
        if not isinstance(value, str):
            current['errors'].append(
                {
                    'message': f'Expected value for {field} to be a '
                    f'string but got {type(value).__name__}.',
                    'field': field,
                    'type': 'ValueError',
                }
            )
            return current
        
        parent_company_os_id_values = split_values(value, self.split_pattern)
        for os_id in parent_company_os_id_values:
            if not self.__is_valid_os_id(os_id):
                current['errors'].append(
                    {
                        'message': f'Expected value for {field} should '
                        f'match OS ID format but got {os_id}',
                        'field': field,
                        'type': 'ValidationError',
                    }
                )

        current[field] = parent_company_os_id_values

        return current
    
    def __is_valid_os_id(self, value: str) -> bool:
        os_id_regex = re.compile('[A-Z]{2}[0-9]{7}[A-Z0-9]{6}')
        return bool(os_id_regex.fullmatch(value))

import re
from contricleaner.lib.helpers.split_values import split_values
from contricleaner.lib.serializers.row_serializers.row_serializer import (
    RowSerializer,
)
from contricleaner.lib.client_abstractions.lookup_interface import (
    LookUpInterface
)
from contricleaner.constants import MAX_PARENT_COMPANY_OS_ID_COUNT


class RowParentCompanyOSIDSerializer(RowSerializer):
    def __init__(
            self,
            os_id_lookup: LookUpInterface,
            split_pattern: str
    ) -> None:
        self.os_id_lookup = os_id_lookup
        self.split_pattern = split_pattern

    def validate(self, row: dict, current: dict) -> dict:
        field = 'parent_company_os_id'
        value = row.get(field)

        if not value:
            return current
        
        if not isinstance(value, (str, list)):
            current['errors'].append(
                {
                    'message': f'Expected value for {field} to be a '
                    f'string or list but got {type(value).__name__}.',
                    'field': field,
                    'type': 'ValueError',
                }
            )
            return current
        
        if isinstance(value, list):
            origin_values = value
        else:
            origin_values = split_values(value, self.split_pattern)
        
        if len(origin_values) > MAX_PARENT_COMPANY_OS_ID_COUNT:
            current['errors'].append(
                {
                    'message': 'You may submit a maximum of {} '
                    'parent_company_os_id, not {}.'.format(
                        MAX_PARENT_COMPANY_OS_ID_COUNT, len(origin_values)
                    ),
                    'field': field,
                    'type': 'ValidationError',
                }
            )
            return current

        valid_os_ids = []
        for os_id in origin_values:
            if not self.__is_valid_os_id(os_id):
                current['errors'].append(
                    {
                        'message': f'Expected value for {field} should '
                        f'match OS ID format but got {os_id}',
                        'field': field,
                        'type': 'ValidationError',
                    }
                )
            else:
                valid_os_ids.append(os_id)
        
        result_map = self.os_id_lookup.bulk_get(
            valid_os_ids
        )
        for key, value in result_map.items():
            if value is None:
                current['errors'].append(
                    {
                        'message': f'The OS ID {key} for {field} '
                        f'does not related to any production location.',
                        'field': field,
                        'type': 'ValidationError',
                    }
                )

        current[field] = origin_values

        return current
    
    def __is_valid_os_id(self, value: str) -> bool:
        os_id_regex = re.compile('[A-Z]{2}[0-9]{7}[A-Z0-9]{6}')
        return bool(os_id_regex.fullmatch(value))

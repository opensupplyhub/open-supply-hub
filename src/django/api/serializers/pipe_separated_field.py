from rest_framework.serializers import (
    ListField,
    ValidationError,
)
from ..processing import (
    remove_empty_array_values,
    strip_array_values
)


class PipeSeparatedField(ListField):
    """Accepts either a list or a pipe-delimited string as input"""

    def to_internal_value(self, data):
        if isinstance(data, str):
            data = data.split('|')
        if ((not isinstance(data, list) or
             any(not isinstance(item, str) for item in data))):
            raise ValidationError(
                'Expected value to be a string or a list of strings '
                f'but got {data}')
        data = remove_empty_array_values(strip_array_values(data))
        return super().to_internal_value(data)

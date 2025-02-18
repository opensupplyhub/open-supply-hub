from rest_framework import serializers


class StringOrListField(serializers.Field):
    """
    Custom field to handle input as either a single string or a
    list of strings.
    """
    def to_internal_value(self, data):
        if isinstance(data, str):
            error = f"Field {self.field_name} can't be an empty string."
            if data:
                return [data]
            else:
                raise serializers.ValidationError(error)

        if isinstance(data, list):
            if not data or any(
                not isinstance(item, str) or item == "" for item in data
            ):
                error = (f"Field {self.field_name} must be a non-empty list "
                         "of valid strings.")
                raise serializers.ValidationError(error)
            return data
        error = (f"Field {self.field_name} must be a string or a "
                 "list of strings.")
        raise serializers.ValidationError(error)

    def to_representation(self, value):
        if isinstance(value, list) and len(value) == 1:
            return value[0]
        else:
            return value

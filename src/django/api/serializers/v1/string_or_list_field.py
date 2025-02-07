from rest_framework import serializers


class StringOrListField(serializers.Field):
    """
    Custom field to handle input as either a single string or a
    list of strings.
    """
    def to_internal_value(self, data):
        if isinstance(data, str):
            error = f"Field {self.field_name} can't be an empty string."

            return [data] if data else self.raise_error(error)

        if isinstance(data, list):
            if not data or any(
                not isinstance(item, str) or item == "" for item in data
            ):
                error = (f"Field {self.field_name} must be a non-empty list "
                         "of valid strings.")
                self.raise_error(error)
            return data
        error = (f"Field {self.field_name} must be a string or a "
                 "list of strings.")
        self.raise_error(error)

    def to_representation(self, value):
        if isinstance(value, list) and len(value) == 1:
            return value[0]
        else:
            return value

    @staticmethod
    def raise_error(message):
        raise serializers.ValidationError(message)

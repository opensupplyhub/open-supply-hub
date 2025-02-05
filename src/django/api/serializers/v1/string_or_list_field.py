from rest_framework import serializers


class StringOrListField(serializers.Field):
    """
    Custom field to handle input as either a single string or a
    list of strings.
    """
    def to_internal_value(self, data):
        if isinstance(data, str):
            return [data] if data else self.raise_error("Field can't be an \
                                                        empty string.")

        if isinstance(data, list):
            if not data or any(
                not isinstance(item, str) or item == "" for item in data
            ):
                self.raise_error(('Field must be a non-empty list of valid '
                                  'strings.'))
            return data

        self.raise_error("Field must be a string or a list of strings.")

    def to_representation(self, value):
        if isinstance(value, list) and len(value) == 1:
            return value[0]
        else:
            return value

    @staticmethod
    def raise_error(message):
        raise serializers.ValidationError(message)

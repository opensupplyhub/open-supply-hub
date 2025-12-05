from rest_framework.serializers import (
    Serializer,
    CharField,
    ValidationError
)


class ISIC4EntrySerializer(Serializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Define 'class' field directly since it's a Python reserved keyword.
        # We can't use it as a class attribute, so we add it in the __init__
        # method.
        self.fields['class'] = CharField(
            required=False,
            allow_blank=False,
            error_messages={
                'blank': 'Field class must be a non-empty string.',
            },
        )

    group = CharField(
        required=False,
        allow_blank=False,
        error_messages={
            'blank': 'Field group must be a non-empty string.',
        },
    )
    section = CharField(
        required=False,
        allow_blank=False,
        error_messages={
            'blank': 'Field section must be a non-empty string.',
        },
    )
    division = CharField(
        required=False,
        allow_blank=False,
        error_messages={
            'blank': 'Field division must be a non-empty string.',
        },
    )

    def to_internal_value(self, data):
        """Override to check for unknown fields before they're dropped."""
        if not isinstance(data, dict):
            raise ValidationError(
                'ISIC-4 entry must be an object.'
            )

        field_names = ('class', 'group', 'section', 'division')

        # Check for unknown fields.
        unknown_fields = set(data.keys()) - set(field_names)
        if unknown_fields:
            errors = {}
            for field in unknown_fields:
                errors[field] = [
                    f'Field {field} is not a valid ISIC-4 field. '
                    f'Only section, division, group, and class '
                    f'are allowed.'
                ]
            raise ValidationError(errors)

        # Check that fields are strings (not numeric or other types).
        errors = {}
        for field_name in field_names:
            if field_name not in data:
                continue
            if not isinstance(data[field_name], str):
                errors[field_name] = [
                    f'Field {field_name} must be a string.'
                ]

        if errors:
            raise ValidationError(errors)

        return super().to_internal_value(data)

    def validate(self, attrs):
        # Check that object is not empty (at least one field required).
        if not attrs:
            raise ValidationError(
                'ISIC-4 object cannot be empty. '
                'At least one field (section, division, group, or '
                'class) must be provided.'
            )

        return attrs

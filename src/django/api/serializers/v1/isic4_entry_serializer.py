from rest_framework import serializers


class ISIC4EntrySerializer(serializers.Serializer):
    isic_class = serializers.CharField(
        source='class',
        required=False,
        allow_blank=False,
        error_messages={
            'required': 'Field class is required for isic_4.',
            'blank': 'Field class must be a non-empty string.',
            'invalid': 'Field class must be a valid string.',
        },
    )
    group = serializers.CharField(
        required=False,
        allow_blank=False,
        error_messages={
            'required': 'Field group is required for isic_4.',
            'blank': 'Field group must be a non-empty string.',
            'invalid': 'Field group must be a valid string.',
        },
    )
    section = serializers.CharField(
        required=False,
        allow_blank=False,
        error_messages={
            'required': 'Field section is required for isic_4.',
            'blank': 'Field section must be a non-empty string.',
            'invalid': 'Field section must be a valid string.',
        },
    )
    division = serializers.CharField(
        required=False,
        allow_blank=False,
        error_messages={
            'required': 'Field division is required for isic_4.',
            'blank': 'Field division must be a non-empty string.',
            'invalid': 'Field division must be a valid string.',
        },
    )

    def validate(self, attrs):
        errors = {}
        raw_data = getattr(self, 'initial_data', {}) or {}
        for field_name in ('class', 'group', 'section', 'division'):
            if field_name not in raw_data:
                continue
            if not isinstance(raw_data[field_name], str):
                errors[field_name] = ['Field '
                                      f'{field_name} must be a string.']
        if errors:
            raise serializers.ValidationError(errors)
        return attrs


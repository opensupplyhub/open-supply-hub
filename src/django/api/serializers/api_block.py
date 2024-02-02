from rest_framework.serializers import (
    ModelSerializer,
    SerializerMethodField,
    ValidationError,
)
from ..models import ApiBlock


class ApiBlockSerializer(ModelSerializer):
    contributor = SerializerMethodField()

    class Meta:
        model = ApiBlock
        fields = ('contributor', 'until', 'active', 'limit', 'actual',
                  'grace_limit', 'grace_created_by', 'grace_reason',
                  'created_at', 'updated_at', 'id')

    def get_contributor(self, instance):
        return instance.contributor.name

    def update(self, instance, validated_data):
        grace_limit = validated_data.get('grace_limit')
        active = validated_data.get('active', instance.active)
        if instance.grace_limit != grace_limit:
            limit = validated_data.get('limit')
            actual = validated_data.get('actual')
            if grace_limit <= limit or grace_limit <= actual:
                raise ValidationError('Grace limit must be greater than ' +
                                      'request limit and actual request ' +
                                      'count.')
            else:
                active = False

        instance.until = validated_data.get('until', instance.until)
        instance.active = active
        instance.limit = validated_data.get('limit', instance.limit)
        instance.actual = validated_data.get('actual', instance.actual)
        instance.grace_limit = validated_data.get('grace_limit',
                                                  instance.grace_limit)
        instance.grace_created_by = validated_data.get(
            'grace_created_by', instance.grace_created_by)
        instance.grace_reason = validated_data.get('grace_reason',
                                                   instance.grace_reason)
        instance.save()

        return instance

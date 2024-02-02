from rest_framework.serializers import (
    HiddenField,
    ModelSerializer,
)
from ...models import ContributorWebhook
from ..user.current_user_contributor import CurrentUserContributor


class ContributorWebhookSerializer(ModelSerializer):
    contributor = HiddenField(default=CurrentUserContributor())

    class Meta:
        model = ContributorWebhook
        fields = ('url', 'notification_type', 'filter_query_string',
                  'contributor', 'created_at', 'updated_at', 'id')
        read_only_fields = ('created_at', 'updated_at')

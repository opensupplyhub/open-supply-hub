from rest_framework.serializers import CurrentUserDefault


class CurrentUserContributor(CurrentUserDefault):
    def __call__(self, serializer_field):
        return super().__call__(serializer_field).contributor

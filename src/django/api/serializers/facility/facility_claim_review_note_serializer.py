from rest_framework.serializers import (
  ModelSerializer,
  SerializerMethodField,
)
from ...models import FacilityClaimReviewNote


class FacilityClaimReviewNoteSerializer(ModelSerializer):
    author = SerializerMethodField()

    class Meta:
        model = FacilityClaimReviewNote
        fields = ('id', 'created_at', 'updated_at', 'note', 'author')

    def get_author(self, note):
        return note.author.email

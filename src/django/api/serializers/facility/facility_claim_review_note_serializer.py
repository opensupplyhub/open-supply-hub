from django.conf import settings
from rest_framework.serializers import (
  ModelSerializer,
  SerializerMethodField,
)
from ...models import FacilityClaimReviewNote


class FacilityClaimReviewNoteSerializer(ModelSerializer):
    author = SerializerMethodField()
    is_automated = SerializerMethodField()

    class Meta:
        model = FacilityClaimReviewNote
        fields = (
            'id', 'created_at', 'updated_at', 'note', 'note_type', 'author',
            'is_automated'
        )

    def get_author(self, note):
        return note.author.email

    def get_is_automated(self, note):
        # Notes written by the claims automation pipeline (LLM review
        # notes, reminder emails sent through message-claimant). Lets
        # consumers distinguish a moderator's ask from an automated
        # nudge — e.g. the v2 dashboard's reply-window stage must not
        # reset when a reminder goes out (OSDEV-3357).
        return note.author.email == settings.CLAIMS_AUTOMATION_ACCOUNT_EMAIL

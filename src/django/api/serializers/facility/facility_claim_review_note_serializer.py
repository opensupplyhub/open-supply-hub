from django.conf import settings
from rest_framework.serializers import (
  ModelSerializer,
  SerializerMethodField,
)
from ...models import FacilityClaimReviewNote


def note_is_automated(note):
    """
    True when the note was written by the claims automation pipeline
    (LLM review notes, reminder emails sent through message-claimant).

    Single definition shared by every serializer that reports it — the
    detail payload's notes and the dashboard list's notes_meta must
    always agree, or the queue rail and the workspace derive different
    stages for the same claim.

    Compared case-insensitively: User.save() lowercases emails on
    write, so a mixed-case setting value would otherwise never match.
    An empty setting disables flagging entirely (nothing is automated).
    """
    configured = (
        settings.CLAIMS_AUTOMATION_ACCOUNT_EMAIL or ''
    ).strip().lower()
    if not configured:
        return False
    return note.author.email.lower() == configured


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
        # Lets consumers distinguish a moderator's ask from an automated
        # nudge — e.g. the v2 dashboard's reply-window stage must not
        # reset when a reminder goes out (OSDEV-3357).
        return note_is_automated(note)

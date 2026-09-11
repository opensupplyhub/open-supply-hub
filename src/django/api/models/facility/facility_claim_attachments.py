from django.db.models import (
    Model,
    BigAutoField,
    CASCADE,
    CharField,
    DateTimeField,
    FileField,
    ForeignKey,
)


class FacilityClaimAttachments(Model):
    '''
    Attachments uploaded by claimant
    '''
    id = BigAutoField(
        auto_created=True,
        primary_key=True,
        serialize=False
    )
    # CASCADE (previously PROTECT): deleting a claim with attachments
    # used to raise ProtectedError, which aborted facility deletion.
    # Django emulates the cascade in Python, so the post_delete signal
    # in api.signals removes the stored file for every cascaded row.
    claim = ForeignKey(
        'FacilityClaim',
        null=False,
        on_delete=CASCADE,
        help_text='The facility claim for this attachment file.'
    )
    file_name = CharField(
        max_length=200,
        null=False,
        blank=False,
        editable=False,
        help_text='The full name of the uploaded claimant attached file.')
    # Stored under an opaque UUID key (see
    # api.helpers.claim_attachments.create_claim_attachment): object
    # keys propagate into access logs and traces, so they must not
    # carry user-supplied filenames.
    claim_attachment = FileField(
        upload_to='claim_attachments/',
        null=True,
        blank=True,
        help_text='The uploaded claimant attached file.'
    )
    uploaded_at = DateTimeField(auto_now_add=True)

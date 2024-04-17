from django.db.models import (
    Model,
    BigAutoField,
    CharField,
    DateTimeField,
    FileField,
    ForeignKey,
    PROTECT,
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
    claim = ForeignKey(
        'FacilityClaim',
        null=False,
        on_delete=PROTECT,
        help_text='The facility claim for this attachment file.'
    )
    file_name = CharField(
        max_length=200,
        null=False,
        blank=False,
        editable=False,
        help_text='The full name of the uploaded claimant attached file.')
    claim_attachment = FileField(
        null=True,
        blank=True,
        help_text='The uploaded claimant attached file.'
    )
    uploaded_at = DateTimeField(auto_now_add=True)

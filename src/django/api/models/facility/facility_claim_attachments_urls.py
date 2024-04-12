from django.db.models import (
    Model,
    BigAutoField,
    ForeignKey,
    DateTimeField,
    URLField,
    PROTECT,
)

class FacilityClaimAttachmentURLs(Model):
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
    claim_attachment_url = URLField(
        null=True,
        blank=True,
        help_text='AWS S3 URL linking to a claimant attached file.'
    )
    uploaded_at = DateTimeField(auto_now_add=True)

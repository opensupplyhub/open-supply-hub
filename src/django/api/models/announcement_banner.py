from django.db.models import BooleanField, DateTimeField, Model
from django_ckeditor_5.fields import CKEditor5Field


class AnnouncementBanner(Model):
    '''
    Site-wide announcement banner shown above the header, managed in the
    Django admin so campaign copy can change without a deploy. A single
    row is seeded by migration; the admin does not allow adding more.
    '''

    is_active = BooleanField(
        default=False,
        help_text=(
            'Whether the banner is currently shown on the site. The banner '
            'only appears when this is ticked and the content is not empty.'
        ),
    )
    content = CKEditor5Field(
        blank=True,
        help_text=(
            'The banner text. Formatting and links are allowed and are '
            'rendered as written.'
        ),
    )

    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Announcement banner'
        verbose_name_plural = 'Announcement banner'

    def __str__(self):
        state = 'active' if self.is_active else 'inactive'
        return f'Announcement banner ({state})'

    def clean(self):
        if self.content:
            cleaned = self.content.strip()
            # Treat the CKEditor empty-document placeholder as no content.
            self.content = '' if cleaned == '<p>&nbsp;</p>' else cleaned

    def save(self, *args, **kwargs):
        self.clean()
        return super().save(*args, **kwargs)

from django.db import models

from api.models.user import User


class IsicTaxonomyConfig(models.Model):
    '''
    Singleton configuration for the ISIC Rev 4 taxonomy used in search filters.

    Only one row (pk=1) should exist. Admins publish spreadsheet uploads to S3
    and toggle frontend visibility via is_active.
    '''

    SINGLETON_PK = 1

    id = models.PositiveSmallIntegerField(
        primary_key=True,
        default=SINGLETON_PK,
        editable=False,
    )
    is_active = models.BooleanField(
        default=False,
        help_text=(
            'When enabled, the ISIC Rev 4 filter is shown in extended search.'
        ),
    )
    version = models.PositiveIntegerField(
        default=0,
        help_text='Monotonic publish version; used in the S3 key prefix.',
    )
    source_file = models.FileField(
        upload_to='taxonomy/isic4/source/',
        null=True,
        blank=True,
        help_text='Most recently uploaded taxonomy spreadsheet.',
    )
    source_filename = models.CharField(
        max_length=255,
        blank=True,
        default='',
        help_text='Original filename from the admin upload, for display only.',
    )
    json_s3_key = models.CharField(
        max_length=512,
        blank=True,
        default='',
        help_text='S3 key for the published isic_rev4.json artifact.',
    )
    bundle_s3_key = models.CharField(
        max_length=512,
        blank=True,
        default='',
        help_text='S3 key for the published isicRev4Taxonomy.js bundle.',
    )
    section_count = models.PositiveIntegerField(default=0)
    division_count = models.PositiveIntegerField(default=0)
    group_count = models.PositiveIntegerField(default=0)
    class_count = models.PositiveIntegerField(default=0)
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='isic_taxonomy_uploads',
        help_text='Staff user who published the active taxonomy version.',
    )
    published_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Timestamp when the active version was published.',
    )
    last_error = models.TextField(
        blank=True,
        default='',
        help_text=(
            'Human-readable failure from the most recent publish attempt.'
        ),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'ISIC taxonomy'
        verbose_name_plural = 'ISIC taxonomies'

    def save(self, *args, **kwargs):
        self.pk = self.SINGLETON_PK
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=cls.SINGLETON_PK)
        return obj

    def __str__(self):
        status = 'active' if self.is_active else 'inactive'
        return (
            f'ISIC taxonomy config v{self.version} ({status}, '
            f'{self.class_count} classes)'
        )

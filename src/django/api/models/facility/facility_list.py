import uuid
from django.db import models
from django.db.models import JSONField

from api.constants import (
    MatchResponsibility,
    OriginSource
)


class FacilityList(models.Model):
    """
    Metadata for an uploaded list of facilities.
    """
    uuid = models.UUIDField(
        null=False,
        default=uuid.uuid4,
        unique=True,
        editable=False,
        help_text='Unique identifier for the facility list.'
    )
    name = models.CharField(
        max_length=200,
        null=False,
        blank=False,
        help_text='The name of list. Defaults to name of the uploaded file.')
    description = models.TextField(
        null=True,
        blank=True,
        help_text='The description of list.')
    file_name = models.CharField(
        max_length=200,
        null=False,
        blank=False,
        editable=False,
        help_text='The full name of the uploaded file.')
    header = models.TextField(
        null=False,
        blank=False,
        editable=False,
        help_text='The header row of the uploaded CSV.')
    replaces = models.OneToOneField(
        'self',
        null=True,
        blank=True,
        unique=True,
        on_delete=models.PROTECT,
        related_name='replaced_by',
        help_text=('If not null this list is an updated version of the '
                   'list specified by this field.'))
    match_responsibility = models.CharField(
        choices=MatchResponsibility.CHOICES,
        default=MatchResponsibility.MODERATOR,
        max_length=12,
        help_text="Who is responsible for moderating this list's data"
    )
    file = models.FileField(
        null=True,
        blank=True,
        help_text='The uploaded file.'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    APPROVED = 'APPROVED'
    PENDING = 'PENDING'
    REJECTED = 'REJECTED'

    MATCHED = 'MATCHED'
    REPLACED = 'REPLACED'

    STATUS_CHOICES = (
        (PENDING, PENDING),
        (APPROVED, APPROVED),
        (REJECTED, REJECTED),
    )
    status = models.CharField(
        max_length=200,
        null=False,
        blank=False,
        choices=STATUS_CHOICES,
        default=PENDING,
        help_text='The current workflow progress of the list.')
    status_change_reason = models.TextField(
        null=False,
        blank=True,
        default='',
        verbose_name='status change reason',
        help_text='The reason entered when changing the status of this list.')
    status_change_by = models.ForeignKey(
        'User',
        null=True,
        on_delete=models.PROTECT,
        verbose_name='status changed by',
        help_text='The user who changed the status of this facility list',
        related_name='approver_of_list')
    parsing_errors = JSONField(
        default=list,
        null=True,
        blank=True,
        help_text=('List-level and internal errors logged during background '
                   'parsing of the list.')
    )
    origin_source = models.CharField(
        choices=OriginSource.CHOICES,
        blank=True,
        null=True,
        max_length=200,
        help_text="The environment value where instance running"
    )

    def __str__(self):
        from ..source import Source
        try:
            if self.source.contributor is None:
                return f'{self.name} ({self.id})'

            return f'{self.source.contributor.name} - {self.name} ({self.id})'
        except Source.DoesNotExist:
            return f'{self.name} [NO SOURCE] ({self.id})'

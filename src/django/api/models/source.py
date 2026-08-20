import uuid
from django.db import models, transaction
from api.constants import OriginSource


class Source(models.Model):
    LIST = 'LIST'
    SINGLE = 'SINGLE'

    SOURCE_TYPE_CHOICES = (
        (LIST, LIST),
        (SINGLE, SINGLE),
    )

    uuid = models.UUIDField(
        null=False,
        default=uuid.uuid4,
        unique=True,
        editable=False,
        help_text='Unique identifier for the source.'
    )
    contributor = models.ForeignKey(
        'Contributor',
        null=True,
        on_delete=models.SET_NULL,
        help_text='The contributor who submitted the facility data'
    )
    source_type = models.CharField(
        null=False,
        max_length=6,
        choices=SOURCE_TYPE_CHOICES,
        help_text='Did the the facility data arrive in a list or a single item'
    )
    facility_list = models.OneToOneField(
        'FacilityList',
        null=True,
        on_delete=models.PROTECT,
        help_text='The related list if the type of the source is LIST.'
    )
    is_active = models.BooleanField(
        null=False,
        default=True,
        help_text=('True if items from the source should be shown as being '
                   'associated with the contributor')
    )
    is_public = models.BooleanField(
        null=False,
        default=True,
        help_text=('True if the public can see factories from this list '
                   'are associated with the contributor.')
    )
    create = models.BooleanField(
        null=False,
        default=True,
        help_text=('Should a facility or facility match be created from the '
                   'facility data')
    )
    is_anonymized = models.BooleanField(
        null=False,
        default=False,
        help_text=('True if the data from this source should be shown '
                   'without identifying the contributor. Unlike is_public, '
                   'the contributed data (names, addresses, sectors, '
                   'extended fields) remains visible.')
    )
    origin_source = models.CharField(
        choices=OriginSource.CHOICES,
        blank=True,
        null=True,
        max_length=200,
        help_text="The environment value where instance running"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def display_name(self):
        name = self.contributor.name \
            if self.contributor else '[Unknown Contributor]'
        if self.facility_list:
            return f'{name} ({self.facility_list.name})'
        return name

    def __str__(self):
        return f'{self.display_name} ({self.id})'

    def save(self, *args, **kwargs):
        """
        Keep extended field attribution in sync with the source.

        Reassigning `contributor` (typically in Django admin) must also
        re-attribute the extended fields contributed through this source,
        otherwise they keep pointing at the original uploader on facility
        detail pages, search responses and downloads. See OSDEV-2159.

        The re-attribution runs in separately committed chunks, so it is
        registered with transaction.on_commit rather than performed here:
        Django admin wraps the whole change view in one transaction, and
        inside it the per-chunk commits would degrade to savepoints of a
        single large transaction, holding locks on api_extendedfield and
        the affected FacilityIndex rows for the entire run. Deferring to
        on_commit means the source row commits first (with the enclosing
        transaction, or immediately in autocommit contexts such as the
        shell) and the chunks then commit one by one — deliberately not
        atomic with the source row. If the enclosing transaction rolls
        back, the callback is discarded along with the contributor
        change, so the two cannot diverge in that direction.
        """
        # Imported lazily to avoid a circular import: the service imports
        # ExtendedField, which is loaded through api.models.
        from api.services.source_service import SourceService

        # `update_fields` is read defensively; when it is passed
        # positionally (deprecated) this falls back to running the check.
        update_fields = kwargs.get('update_fields')
        contributor_may_change = (
            not self._state.adding
            and (update_fields is None or 'contributor' in update_fields)
        )
        if not contributor_may_change:
            return super().save(*args, **kwargs)

        previous_contributor_id = (
            Source.objects
            .filter(pk=self.pk)
            .values_list('contributor_id', flat=True)
            .first()
        )

        result = super().save(*args, **kwargs)
        if previous_contributor_id != self.contributor_id:
            transaction.on_commit(
                lambda: SourceService.reassign_extended_fields(self)
            )
        return result

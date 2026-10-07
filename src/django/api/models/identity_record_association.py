import uuid

from django.core.validators import URLValidator
from django.db import models
from simple_history.models import HistoricalRecords

from api.constants import OriginSource


class IdentityRecordAssociation(models.Model):
    """
    Links an OS ID to an external Resolver URI for a record published about
    that location by another organization.

    Open Supply Hub stores the association and nothing else. No credential
    body is copied, cached or re-published (NFR-04, scope doc 2.4). The
    stored value is always the issuer's Resolver URI and never a Credential
    URL, which is what allows the always-current guarantee in 3.3 to hold
    without synchronization between the two organizations (FR-06).
    """

    class Meta:
        verbose_name = 'identity record association'
        verbose_name_plural = 'identity record associations'
        constraints = [
            models.UniqueConstraint(
                fields=['os_id', 'resolver_uri'],
                name='unique_os_id_resolver_uri',
            ),
        ]
        indexes = [
            models.Index(fields=['os_id'], name='idr_assoc_os_id_idx'),
        ]

    uuid = models.UUIDField(
        null=False,
        default=uuid.uuid4,
        unique=True,
        editable=False,
        help_text='Unique identifier for the association.'
    )
    # Deliberately a plain identifier rather than a ForeignKey to Facility.
    # An OS ID can be superseded when two locations are merged, and the
    # superseded identifier keeps resolving to the surviving record through
    # FacilityAlias. Storing the identifier rather than a row reference
    # means a merge does not touch this table at all, and resolution follows
    # the alias on read, which is the behaviour Section 2.7 promises to RBA.
    os_id = models.CharField(
        max_length=32,
        null=False,
        help_text=('The OS ID the record is registered against. Not a '
                   'foreign key: see the note in the model source.')
    )
    resolver_uri = models.TextField(
        null=False,
        validators=[URLValidator(schemes=['https'])],
        help_text=('The issuer\'s Resolver URI for the record. Must be an '
                   'absolute HTTPS URI. Never a Credential URL, which points '
                   'at one specific version and would break the '
                   'always-current guarantee (FR-06).')
    )
    record_type = models.CharField(
        max_length=200,
        null=False,
        help_text=('The type of record held at the Resolver URI, for '
                   'example untp:DigitalFacilityRecord.')
    )
    issuer = models.CharField(
        max_length=500,
        null=False,
        help_text=('Identifier of the organization that issued the record, '
                   'for example a did:web value.')
    )
    registrant_reference = models.CharField(
        max_length=200,
        null=False,
        blank=True,
        help_text=('The registrant\'s own identifier for the location, kept '
                   'so they can reconcile against their register.')
    )
    live_from = models.DateTimeField(
        null=True,
        blank=True,
        help_text=('When this association began resolving. Null while a '
                   'registration is pending; set when it goes live. '
                   'Pilot-set registrations are live on creation '
                   '(Section 3.2).')
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

    history = HistoricalRecords(
        excluded_fields=['uuid', 'origin_source']
    )

    @property
    def is_live(self):
        return self.live_from is not None

    def __str__(self):
        return f'{self.os_id} -> {self.resolver_uri}'

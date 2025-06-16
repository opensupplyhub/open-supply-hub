import uuid
from django.contrib.gis.db import models as gis_models
from django.contrib.postgres import fields as postgres
from django.contrib.postgres.indexes import GinIndex
from django.db import models

from countries.lib.countries import COUNTRY_CHOICES
from ..contributor.contributor import Contributor
from .facility_manager_index_new import FacilityIndexNewManager


class FacilityIndex(models.Model):
    """
    Stores denormalized indexes for the facility's name, id, contributors_count
    """
    id = models.CharField(
        max_length=32,
        primary_key=True,
        editable=False,
        db_index=True,
        help_text='The OS ID of a facility.')
    uuid = models.UUIDField(
        null=False,
        default=uuid.uuid4,
        editable=False,
        unique=True,
        help_text='Unique identifier for the facility index.'
    )
    name = models.CharField(
        max_length=200,
        null=False,
        blank=False,
        db_index=True,
        help_text='The name of the facility.')
    address = models.CharField(
        max_length=200,
        null=False,
        blank=False,
        db_index=True,
        help_text='The full street address of the facility.')
    country_code = models.CharField(
        max_length=2,
        null=False,
        blank=False,
        db_index=True,
        choices=COUNTRY_CHOICES,
        help_text='The ISO 3166-1 alpha-2 country code of the facility.')
    location = gis_models.PointField(
        null=False,
        help_text='The lat/lng point location of the facility')
    contributors_count = models.IntegerField(
        null=False,
        blank=False,
        db_index=True,
        help_text='The count of the public contributors.')
    contributors_id = postgres.ArrayField(models.IntegerField(
        null=True,
        help_text='The contributor id who submitted the facility data.'))
    approved_claim_ids = postgres.ArrayField(models.IntegerField(
        null=True,
        editable=False,
        db_index=True,
        default=list,
        help_text='The related approved claim facilities.'))
    is_closed = models.BooleanField(
        null=True,
        db_index=True,
        help_text=('Whether this facility is closed.')
    )
    new_os_id = models.CharField(
        max_length=32,
        null=True,
        blank=True,
        help_text=('The new OS ID where this facility can be found if it '
                   'has been moved.'))
    has_inexact_coordinates = models.BooleanField(
        null=False,
        default=False,
        help_text=('Whether this facility has manually adjusted coordinates '
                   'known to be inexact.')
    )
    contrib_types = postgres.ArrayField(models.CharField(
        max_length=2000,
        null=True,
        blank=False,
        db_index=True,
        choices=Contributor.CONTRIB_TYPE_CHOICES,
        help_text='The categories to which the contributors belong.'))
    contributors = postgres.ArrayField(models.JSONField(
        help_text='The contributor who submitted the facility data.'))
    sector = postgres.ArrayField(models.CharField(
        max_length=50,
        null=False,
        blank=False,
        db_index=True,
        help_text='The sector(s) for goods made at the facility',
    ), default=list)
    lists = postgres.ArrayField(models.IntegerField(
        null=True,
        editable=False,
        db_index=True,
        help_text='The related list if the type of the source is LIST.'))
    custom_text = postgres.ArrayField(models.TextField(
        null=False,
        blank=False,
        db_index=True,
        help_text='A collection of custom values to search for the '
                  'facility'),
        default=list)
    custom_text_search = models.TextField(
        blank=False,
        help_text=('A concatenated string of custom values for searching'
                   'the facility in accent-insensitive and accent-sensitive'
                   'lookup modes.'),
        default='')
    number_of_workers = postgres.ArrayField(models.TextField(
        null=False,
        blank=False,
        db_index=True,
        help_text='ExtendedField for number of workers.'),
        default=list)
    facility_type = postgres.ArrayField(models.CharField(
        max_length=2000,
        null=False,
        blank=False,
        db_index=True,
        help_text='ExtendedField for facility type.'),
        default=list)
    processing_type = postgres.ArrayField(models.CharField(
        max_length=2000,
        null=False,
        blank=False,
        db_index=True,
        help_text='ExtendedField for processing type.'),
        default=list)
    product_type = postgres.ArrayField(models.CharField(
        max_length=2000,
        null=False,
        blank=False,
        db_index=True,
        help_text='ExtendedField for product type.'),
        default=list)
    parent_company_name = postgres.ArrayField(models.CharField(
        max_length=2000,
        null=False,
        blank=False,
        db_index=True,
        help_text='ExtendedField for parent company.'),
        default=list)
    native_language_name = postgres.ArrayField(models.CharField(
        max_length=2000,
        null=False,
        blank=False,
        db_index=True,
        help_text='ExtendedField for native language name.'),
        default=list)
    parent_company_id = postgres.ArrayField(models.IntegerField(
        null=False,
        blank=False,
        db_index=True,
        help_text='ExtendedField for parent_company_id.'),
        default=list)
    facility_names = postgres.ArrayField(models.JSONField(
        help_text='List of facility names for given facility.', default=list))
    facility_list_items = postgres.ArrayField(models.JSONField(
        help_text='List of facility list items assigneg to this facility.'),
        default=list
        )
    facility_locations = postgres.ArrayField(models.JSONField(
        help_text='The corrected location info of the facility.'),
        default=list
        )
    approved_claim = models.JSONField(
        help_text='List of facility list items assigneg to this facility.',
        blank=True,
        null=True
        )
    facility_addresses = postgres.ArrayField(models.JSONField(
        help_text='List of facility addresses for given facility.'))
    claim_info = models.JSONField(
        help_text='Claim information for given facility.',
        null=True,
        )
    custom_field_info = postgres.ArrayField(models.JSONField(
        help_text='Embed Field information for given facility.'),
        default=list
        )
    extended_fields = postgres.ArrayField(models.JSONField(
        help_text='The extended fields for given facility.'))
    created_from_info = models.JSONField(
        help_text=('The original uploaded list item info from which this '
                   'facility was created.'),
        blank=True,
        null=True
        )
    activity_reports_info = postgres.ArrayField(models.JSONField(
        help_text='Activity Reports information for given facility.'),
        default=list
        )
    item_sectors = postgres.ArrayField(models.JSONField(
        help_text="Items' sectors information for given facility."),
        default=list
        )
    claim_sectors = postgres.ArrayField(models.JSONField(
        help_text="Claims' sectors information for given facility."),
        default=list
        )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    objects = FacilityIndexNewManager()

    class Meta:
        indexes = [GinIndex(
            fields=['contrib_types', 'contributors_id', 'lists']
        )]

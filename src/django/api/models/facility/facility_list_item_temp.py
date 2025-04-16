from api.models.transactions.index_facilities_new import index_facilities_new

from django.contrib.gis.db import models as gis_models
from django.contrib.postgres import fields as postgres
from django.db import models

from countries.lib.countries import COUNTRY_CHOICES


def hooked_index_facilities(**kwargs):
    instance = kwargs.get('instance')
    if instance.facility is not None:
        statuses = [
            FacilityListItemTemp.MATCHED,
            FacilityListItemTemp.CONFIRMED_MATCH
        ]
        if instance.status in statuses:
            index_facilities_new([instance.facility_id])


class FacilityListItemTemp(models.Model):
    """
    [A/B Test model] Data, metadata, and workflow status and results for
    a single line from a facility list file.
    """
    UPLOADED = 'UPLOADED'
    PARSED = 'PARSED'
    DUPLICATE = 'DUPLICATE'
    GEOCODED = 'GEOCODED'
    GEOCODED_NO_RESULTS = 'GEOCODED_NO_RESULTS'
    MATCHED = 'MATCHED'
    POTENTIAL_MATCH = 'POTENTIAL_MATCH'
    CONFIRMED_MATCH = 'CONFIRMED_MATCH'
    ERROR = 'ERROR'
    ERROR_PARSING = 'ERROR_PARSING'
    ERROR_GEOCODING = 'ERROR_GEOCODING'
    ERROR_MATCHING = 'ERROR_MATCHING'
    DELETED = 'DELETED'
    ITEM_REMOVED = 'ITEM_REMOVED'

    # NEW_FACILITY is a meta status. If the `status` of a `FacilityListItem` is
    # `MATCHED` or `CONFIRMED_MATCH` and the `facility` was `created_from` the
    # `FacilityListItem` then the item represents a new facility.
    NEW_FACILITY = 'NEW_FACILITY'

    # REMOVED is also a meta status. A `FacilityListItem` has been removed if
    # any of its `FacilityMatch`es have `is_active` set to False.
    REMOVED = 'REMOVED'

    # These status choices must be kept in sync with the client's
    # If a new status is added, add supporting styles src/react/src/App.css
    # `facilityListItemStatusChoicesEnum`.
    STATUS_CHOICES = (
        (UPLOADED, UPLOADED),
        (PARSED, PARSED),
        (DUPLICATE, DUPLICATE),
        (GEOCODED, GEOCODED),
        (GEOCODED_NO_RESULTS, GEOCODED_NO_RESULTS),
        (MATCHED, MATCHED),
        (POTENTIAL_MATCH, POTENTIAL_MATCH),
        (CONFIRMED_MATCH, CONFIRMED_MATCH),
        (ERROR, ERROR),
        (ERROR_PARSING, ERROR_PARSING),
        (ERROR_GEOCODING, ERROR_GEOCODING),
        (ERROR_MATCHING, ERROR_MATCHING),
        (DELETED, DELETED),
        (ITEM_REMOVED, ITEM_REMOVED)
    )

    ERROR_STATUSES = [ERROR, ERROR_PARSING, ERROR_GEOCODING, ERROR_MATCHING,
                      DUPLICATE]
    COMPLETE_STATUSES = [MATCHED, CONFIRMED_MATCH]

    class Meta:
        indexes = [
            models.Index(fields=['source', 'row_index'],
                         name='api_flit_facility_list_row_idx'),
            models.Index(fields=['country_code', 'clean_name',
                                 'clean_address'],
                         name='api_flit_match_fields_idx')
        ]

    source = models.ForeignKey(
        'Source',
        null=False,
        on_delete=models.PROTECT,
        help_text='The source from which this item was created.'
    )
    row_index = models.IntegerField(
        null=False,
        editable=False,
        help_text='Index of this line in the CSV file.')
    raw_data = models.TextField(
        null=False,
        blank=False,
        help_text='The full, unparsed CSV line as it appeared in the file.')
    status = models.CharField(
        max_length=200,
        null=False,
        blank=False,
        choices=STATUS_CHOICES,
        default=UPLOADED,
        help_text='The current workflow progress of the line item.')
    processing_started_at = models.DateTimeField(
        null=True,
        help_text=('When background processing of this item started. '
                   'Items awaiting processing will have a null value.'))
    processing_completed_at = models.DateTimeField(
        null=True,
        help_text=('When background processing of this item finished. '
                   'Items awaiting or in process will have a null value.'))
    processing_results = models.JSONField(
        default=list,
        help_text=('Diagnostic details logged by background processing '
                   'including details returned from the geocoder.'))
    name = models.CharField(
        max_length=200,
        null=False,
        blank=False,
        help_text='The name of the facility taken from the raw data.')
    address = models.CharField(
        max_length=200,
        null=False,
        blank=False,
        help_text='The address of the facility taken from the raw data.')
    country_code = models.CharField(
        max_length=2,
        null=False,
        blank=False,
        choices=COUNTRY_CHOICES,
        help_text=('The ISO 3166-1 alpha-2 country code of the facility taken '
                   'directly from the raw data or looked up based on a full '
                   'country name provided in the raw data.'))
    sector = postgres.ArrayField(
        models.CharField(max_length=50, null=False, blank=False),
        help_text='The sector(s) for goods made at the facility',
    )
    geocoded_point = gis_models.PointField(
        null=True,
        help_text=('The geocoded location the facility address field taken '
                   'from the raw data.'))
    geocoded_address = models.CharField(
        max_length=1000,
        null=True,
        blank=True,
        help_text='The geocoded address of the facility.')
    facility_id = models.CharField(
        max_length=200,
        null=True,
        blank=False,
        help_text=('The facility created from this list item or the '
                   'previously existing facility to which this list '
                   'item was matched.'))
    clean_name = models.CharField(
        max_length=2000,
        null=False,
        blank=False,
        default='',
        help_text='The cleaned name of the facility.')
    clean_address = models.CharField(
        max_length=2000,
        null=False,
        blank=False,
        default='',
        help_text='The cleaned address of the facility.')
    version = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        help_text='The version of Dedupe Hub instance that used.')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def has_active_complete_match(self):
        from .facility_match_temp import FacilityMatchTemp
        return self.facilitymatchtemp_set.filter(
            is_active=True,
            status__in=[
                FacilityMatchTemp.AUTOMATIC,
                FacilityMatchTemp.CONFIRMED,
                FacilityMatchTemp.MERGED
            ]
        ).count() > 0

    def __str__(self):
        return 'FacilityListItemTemp {id} - {status}'.format(**self.__dict__)

    @staticmethod
    def post_save(sender, **kwargs):
        pass
        # hooked_index_facilities(**kwargs)

    @staticmethod
    def post_delete(sender, **kwargs):
        pass
        # hooked_index_facilities(**kwargs)

    @staticmethod
    def copy(item):
        FacilityListItemTemp.objects.create(
            id=item.id,
            source=item.source,
            facility_id=item.facility_id,
            geocoded_point=item.geocoded_point,
            geocoded_address=item.geocoded_address,
            row_index=item.row_index,
            raw_data=item.raw_data,
            status=item.status,
            name=item.name,
            clean_name=item.clean_name,
            address=item.address,
            clean_address=item.clean_address,
            country_code=item.country_code,
            sector=item.sector,
            processing_results=item.processing_results,
            processing_started_at=item.processing_started_at,
            processing_completed_at=item.processing_completed_at
        )

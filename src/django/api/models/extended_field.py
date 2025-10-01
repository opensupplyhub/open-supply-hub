import uuid
from simple_history.models import HistoricalRecords
from django.db import models
from api.constants import OriginSource


class ExtendedField(models.Model):
    """
    Extended data fields available to include on facilities.
    Fields will be related to either a claim or list item; they must reference
    one, but not both.
    """
    NAME = 'name'
    ADDRESS = 'address'
    NUMBER_OF_WORKERS = 'number_of_workers'
    NATIVE_LANGUAGE_NAME = 'native_language_name'
    FACILITY_TYPE = 'facility_type'
    PROCESSING_TYPE = 'processing_type'
    PRODUCT_TYPE = 'product_type'
    PARENT_COMPANY = 'parent_company'
    PARENT_COMPANY_OS_ID = 'parent_company_os_id'
    DUNS_ID = 'duns_id'
    LEI_ID = 'lei_id'
    RBA_ID = 'rba_id'
    ESTIMATED_EMISSIONS_ACTIVITY = 'estimated_emissions_activity'
    ESTIMATED_ANNUAL_ENERGY_CONSUMPTION = 'estimated_annual_energy_consumption'

    FIELD_CHOICES = (
        (NAME, NAME),
        (ADDRESS, ADDRESS),
        (NUMBER_OF_WORKERS, NUMBER_OF_WORKERS),
        (NATIVE_LANGUAGE_NAME, NATIVE_LANGUAGE_NAME),
        (FACILITY_TYPE, FACILITY_TYPE),
        (PROCESSING_TYPE, PROCESSING_TYPE),
        (PRODUCT_TYPE, PRODUCT_TYPE),
        (PARENT_COMPANY, PARENT_COMPANY),
        (PARENT_COMPANY_OS_ID, PARENT_COMPANY_OS_ID),
        (DUNS_ID, DUNS_ID),
        (LEI_ID, LEI_ID),
        (RBA_ID, RBA_ID),
        (
            ESTIMATED_EMISSIONS_ACTIVITY,
            ESTIMATED_EMISSIONS_ACTIVITY
        ),
        (
            ESTIMATED_ANNUAL_ENERGY_CONSUMPTION,
            ESTIMATED_ANNUAL_ENERGY_CONSUMPTION
        )
    )

    uuid = models.UUIDField(
        null=False,
        default=uuid.uuid4,
        unique=True,
        editable=False,
        help_text='Unique identifier for the extended field.'
    )
    contributor = models.ForeignKey(
        'Contributor',
        null=False,
        on_delete=models.CASCADE,
        help_text='The contributor who submitted this field'
    )
    facility = models.ForeignKey(
        'Facility',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        help_text='The facility to which this field belongs.'
    )
    facility_list_item = models.ForeignKey(
        'FacilityListItem',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        help_text='The list item from which the field was obtained.')
    facility_claim = models.ForeignKey(
        'FacilityClaim',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        help_text='The claim from which the field was obtained.')
    is_verified = models.BooleanField(
        default=False,
        null=False,
        help_text='Whether or not this field has been verified.'
    )
    field_name = models.CharField(
        max_length=200,
        null=False,
        blank=False,
        choices=FIELD_CHOICES,
        help_text='The name of the field, chosen from a strict list.')
    value = models.JSONField(
        null=False,
        blank=False,
        help_text=('The value of the field. An  object with different '
                   'structure for different fields.'
                   'Numeric fields are stored as {"min": 1, "max": 2}.'
                   'If there is a single numeric value, set both min '
                   'and max to it.'))
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

    def __str__(self):
        return (
            f"{self.field_name} - {self.facility_id} "
            f"- {self.contributor.name} ({self.id})"
        )

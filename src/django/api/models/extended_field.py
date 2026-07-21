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
    ISIC_4 = 'isic_4'

    # --- Data center attribute fields (see OSDEV-2568 / OSDEV-3066) ---
    # Named entities
    NAME_UNSPECIFIED = 'name_unspecified'
    NAME_SITE_OTHER = 'name_site_other'
    NAME_OWNER = 'name_owner'
    NAME_PROPERTY_MANAGER = 'name_property_manager'
    NAME_OPERATOR = 'name_operator'
    NAME_PERMIT_HOLDER = 'name_permit_holder'
    NAME_BUILDING_OWNER = 'name_building_owner'
    NAME_TENANT = 'name_tenant'
    # Utility usage
    CAPACITY = 'capacity'
    CAPACITY_UNITS = 'capacity_units'
    IT_CAPACITY = 'it_capacity'
    IT_CAPACITY_UNITS = 'it_capacity_units'
    UTILITY_CAPACITY = 'utility_capacity'
    UTILITY_CAPACITY_UNITS = 'utility_capacity_units'
    UPS_CAPACITY = 'ups_capacity'
    UPS_CAPACITY_UNITS = 'ups_capacity_units'
    BACKUP_GENERATOR_CAPACITY = 'backup_generator_capacity'
    BACKUP_GENERATOR_CAPACITY_UNITS = 'backup_generator_capacity_units'
    PUE = 'pue'
    POWER_PROVIDERS = 'power_providers'
    POWER_SOURCES = 'power_sources'
    POWER_DENSITY = 'power_density'
    POWER_DENSITY_UNITS = 'power_density_units'
    WATER_USAGE = 'water_usage'
    WATER_USAGE_UNITS = 'water_usage_units'
    WUE = 'wue'
    COOLING_MECHANISM = 'cooling_mechanism'
    # Operating info
    OPERATIONAL_STATUS = 'operational_status'
    CERTIFICATIONS_COMPLIANCE = 'certifications_compliance'
    TIME_ZONES = 'time_zones'
    DATE_OPERATIONAL = 'date_operational'
    # Building info
    AREA = 'area'
    AREA_UNITS = 'area_units'
    DATA_AREA = 'data_area'
    DATA_AREA_UNITS = 'data_area_units'
    FLOOR_SPACE = 'floor_space'
    FLOOR_SPACE_UNITS = 'floor_space_units'
    OVERALL_AREA = 'overall_area'
    OVERALL_AREA_UNITS = 'overall_area_units'
    OTHER_AREA = 'other_area'
    OTHER_AREA_NOTES = 'other_area_notes'
    OTHER_AREA_UNITS = 'other_area_units'
    NUMBER_OF_SERVERS = 'number_of_servers'
    NUMBER_OF_RACKS = 'number_of_racks'

    # Data center fields grouped for reuse in ingestion (see extended_fields.py)
    DATA_CENTER_FIELDS = (
        NAME_UNSPECIFIED, NAME_SITE_OTHER, NAME_OWNER, NAME_PROPERTY_MANAGER,
        NAME_OPERATOR, NAME_PERMIT_HOLDER, NAME_BUILDING_OWNER, NAME_TENANT,
        CAPACITY, CAPACITY_UNITS, IT_CAPACITY, IT_CAPACITY_UNITS,
        UTILITY_CAPACITY, UTILITY_CAPACITY_UNITS, UPS_CAPACITY,
        UPS_CAPACITY_UNITS, BACKUP_GENERATOR_CAPACITY,
        BACKUP_GENERATOR_CAPACITY_UNITS, PUE, POWER_PROVIDERS, POWER_SOURCES,
        POWER_DENSITY, POWER_DENSITY_UNITS, WATER_USAGE, WATER_USAGE_UNITS,
        WUE, COOLING_MECHANISM, OPERATIONAL_STATUS, CERTIFICATIONS_COMPLIANCE,
        TIME_ZONES, DATE_OPERATIONAL, AREA, AREA_UNITS, DATA_AREA,
        DATA_AREA_UNITS, FLOOR_SPACE, FLOOR_SPACE_UNITS, OVERALL_AREA,
        OVERALL_AREA_UNITS, OTHER_AREA, OTHER_AREA_NOTES, OTHER_AREA_UNITS,
        NUMBER_OF_SERVERS, NUMBER_OF_RACKS,
    )

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
        (ISIC_4, ISIC_4),
    ) + tuple((f, f) for f in DATA_CENTER_FIELDS)

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

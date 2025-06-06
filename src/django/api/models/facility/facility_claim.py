from collections import defaultdict

from simple_history.models import HistoricalRecords
from django.contrib.gis.db import models as gis_models
from django.contrib.postgres import fields as postgres
from django.db import models

from countries.lib.countries import COUNTRY_CHOICES
from api.constants import (
    FacilityClaimStatuses,
    OriginSource
)
from ...constants import Affiliations, Certifications
from ...facility_type_processing_type import ALL_FACILITY_TYPE_CHOICES


class FacilityClaim(models.Model):
    """
    Data submitted from a user attempting to make a verified claim of a
    Facility to be evaluated by OS Hub moderators.
    """

    # These status choices must be kept in sync with the client's
    # `facilityClaimStatusChoicesEnum`.
    STATUS_CHOICES = (
        (FacilityClaimStatuses.PENDING, FacilityClaimStatuses.PENDING),
        (FacilityClaimStatuses.APPROVED, FacilityClaimStatuses.APPROVED),
        (FacilityClaimStatuses.DENIED, FacilityClaimStatuses.DENIED),
        (FacilityClaimStatuses.REVOKED, FacilityClaimStatuses.REVOKED),
    )

    CUT_AND_SEW = 'Cut and Sew / RMG'
    DYEHOUSE = 'Dyehouse'
    EMBELLISHMENTS = 'Embellishments'
    FABRIC_MILL = 'Fabric Mill'
    FINISHING = 'Finishing'
    GINNING = 'Ginning'
    KNITTING = 'Knitting'
    LAUNDRY = 'Laundry'
    PACKING = 'Packing'
    SCOURING = 'Scouring'
    SCREENPRINTING = 'Screenprinting'
    STITCHING = 'Stitching (Shoes)'
    TANNERY = 'Tannery'
    WAREHOUSE = 'Warehouse'
    WEAVING = 'Weaving'
    OTHER = 'Other'

    FACILITY_TYPE_CHOICES = (
        (CUT_AND_SEW, CUT_AND_SEW),
        (DYEHOUSE, DYEHOUSE),
        (EMBELLISHMENTS, EMBELLISHMENTS),
        (FABRIC_MILL, FABRIC_MILL),
        (FINISHING, FINISHING),
        (GINNING, GINNING),
        (KNITTING, KNITTING),
        (LAUNDRY, LAUNDRY),
        (PACKING, PACKING),
        (SCOURING, SCOURING),
        (SCREENPRINTING, SCREENPRINTING),
        (STITCHING, STITCHING),
        (TANNERY, TANNERY),
        (WAREHOUSE, WAREHOUSE),
        (WEAVING, WEAVING),
        (OTHER, OTHER),
    )

    AFFILIATION_CHOICES = [
        (choice, choice)
        for choice in
        [
            Affiliations.BENEFITS_BUSINESS_WORKERS,
            Affiliations.BETTER_MILLS_PROGRAM,
            Affiliations.BETTER_WORK,
            Affiliations.CANOPY,
            Affiliations.ETHICAL_TRADING_INITIATIVE,
            Affiliations.FAIR_LABOR_ASSOCIATION,
            Affiliations.FAIR_WEAR_FOUNDATION,
            Affiliations.HERFINANCE,
            Affiliations.HERHEATH,
            Affiliations.HERRESPECT,
            Affiliations.SEDEX,
            Affiliations.SOCIAL_LABOR_CONVERGENCE_PLAN,
            Affiliations.SUSTAINABLE_APPAREL_COALITION,
            Affiliations.SWEATFREE_PURCHASING_CONSORTIUM,
            Affiliations.ZDHC,
        ]
    ]

    CERTIFICATION_CHOICES = [
        (choice, choice)
        for choice in
        [
            Certifications.BCI,
            Certifications.B_CORP,
            Certifications.BLUESIGN,
            Certifications.CANOPY,
            Certifications.CRADLE_TO_CRADLE,
            Certifications.EU_ECOLABEL,
            Certifications.FAIRTRADE_USA,
            Certifications.FSC,
            Certifications.GLOBAL_RECYCLING_STANDARD,
            Certifications.GOTS,
            Certifications.GREEN_BUTTON,
            Certifications.GREEN_SCREEN,
            Certifications.HIGG_INDEX,
            Certifications.IMO_CONTROL,
            Certifications.INTERNATIONAL_WOOL_TEXTILE,
            Certifications.ISO_9000,
            Certifications.IVN_LEATHER,
            Certifications.LEATHER_WORKING_GROUP,
            Certifications.NORDIC_SWAN,
            Certifications.OEKO_TEX_STANDARD,
            Certifications.OEKO_TEX_STEP,
            Certifications.OEKO_TEX_ECO_PASSPORT,
            Certifications.OEKO_TEX_MADE_IN_GREEN,
            Certifications.PEFC,
            Certifications.REACH,
            Certifications.RESPONSIBLE_DOWN_STANDARD,
            Certifications.RESPONSIBLE_WOOL_STANDARD,
            Certifications.SAB8000,
        ]
    ]

    contributor = models.ForeignKey(
        'Contributor',
        null=False,
        on_delete=models.PROTECT,
        help_text='The contributor who submitted this facility claim')
    facility = models.ForeignKey(
        'Facility',
        null=False,
        on_delete=models.PROTECT,
        help_text='The facility for which this claim has been submitted')
    contact_person = models.CharField(
        max_length=200,
        null=False,
        blank=False,
        verbose_name='contact person',
        help_text='The contact person for the facility claim')
    job_title = models.CharField(
        max_length=200,
        null=False,
        blank=False,
        help_text='The contact person\'s job title',
        verbose_name='contact person\'s job title',
        default='')
    company_name = models.CharField(
        max_length=200,
        null=False,
        blank=True,
        verbose_name='company name',
        help_text='The company name for the facility')
    website = models.CharField(
        max_length=200,
        null=False,
        blank=True,
        verbose_name='website',
        help_text='The website for the facility')
    facility_description = models.TextField(
        null=False,
        blank=False,
        verbose_name='description',
        help_text='A description of the facility')
    linkedin_profile = models.URLField(
        null=False,
        blank=True,
        help_text='A LinkedIn profile for verifying the facility claim',
        verbose_name='verification LinkedIn profile')
    status = models.CharField(
        max_length=200,
        null=False,
        blank=False,
        choices=STATUS_CHOICES,
        default=FacilityClaimStatuses.PENDING,
        verbose_name='status',
        help_text='The current status of this facility claim')
    status_change_reason = models.TextField(
        null=True,
        blank=True,
        verbose_name='status change reason',
        help_text='The reason entered when changing the status of this claim.')
    status_change_by = models.ForeignKey(
        'User',
        null=True,
        on_delete=models.PROTECT,
        verbose_name='status changed by',
        help_text='The user who changed the status of this facility claim',
        related_name='approver_of_claim')
    status_change_date = models.DateTimeField(
        null=True,
        verbose_name='status change date',
    )
    facility_name_english = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        help_text='Not editable official English facility name for the claim.',
        verbose_name='facility name in English')
    facility_name_native_language = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        help_text='The editable official native language facility name.',
        verbose_name='facility name in native language')
    facility_address = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name='address',
        help_text='Not editable facility address for this claim.')
    facility_location = gis_models.PointField(
        null=True,
        verbose_name='location',
        help_text='The lat/lng point location of the facility')
    facility_phone_number = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name='facility phone number',
        help_text='The editable facility phone number for this claim.')
    facility_phone_number_publicly_visible = models.BooleanField(
        null=False,
        default=False,
        verbose_name='is facility phone number publicly visible',
        help_text='Is the editable facility phone number publicly visible?')
    facility_website = models.URLField(
        null=True,
        blank=True,
        verbose_name='facility website',
        help_text='The editable facility website for this claim.')
    facility_website_publicly_visible = models.BooleanField(
        null=False,
        default=False,
        help_text='Is the website publicly visible?',
        verbose_name='facility website visible')
    facility_minimum_order_quantity = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name='minimum order quantity',
        help_text='The editable facility min order quantity for this claim.')
    facility_average_lead_time = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name='average lead time',
        help_text='The editable facilty avg lead time for this claim.')
    facility_workers_count = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name='facility workers count',
        help_text='The editable facility workers count for this claim')
    facility_female_workers_percentage = models.IntegerField(
        null=True,
        blank=True,
        choices=[(i, i) for i in range(0, 101)],
        help_text=('Integer value indicating the facility\'s percentage of '
                   'female workers.'),
        verbose_name='percentage of female workers')
    facility_affiliations = postgres.ArrayField(
        models.CharField(
            null=False,
            blank=False,
            choices=AFFILIATION_CHOICES,
            max_length=50,
            help_text='A group the facility is affiliated with',
            verbose_name='facility affiliation',
        ),
        null=True,
        blank=True,
        help_text='The facility\'s affiliations',
        verbose_name='facility affilations',
    )
    facility_certifications = postgres.ArrayField(
        models.CharField(
            null=False,
            blank=False,
            choices=CERTIFICATION_CHOICES,
            max_length=50,
            help_text='A certification the facility has achieved',
            verbose_name='facility certification',
        ),
        null=True,
        blank=True,
        help_text='The facility\'s certifications',
        verbose_name='facility certifications',
    )
    facility_type = models.CharField(
        max_length=300,
        null=True,
        blank=True,
        choices=ALL_FACILITY_TYPE_CHOICES,
        help_text='The editable facility type for this claim.',
        verbose_name='facility type')
    other_facility_type = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        help_text='Editable alternate text when facility type is OTHER.',
        verbose_name='description of other facility type')
    facility_product_types = postgres.ArrayField(
        models.CharField(
            null=False,
            blank=False,
            max_length=50,
            help_text='A product produced at the facility',
            verbose_name='product type',
        ),
        null=True,
        blank=True,
        help_text='The products produced at the facility',
        verbose_name='product types',
    )
    facility_production_types = postgres.ArrayField(
        models.CharField(
            null=False,
            blank=False,
            max_length=50,
            help_text='A processing type associated with the facility',
            verbose_name='processing type',
        ),
        null=True,
        blank=True,
        help_text='The processing types associated with the facility',
        verbose_name='processing types',
    )
    point_of_contact_person_name = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name='contact person',
        help_text='The editable point of contact person name')
    point_of_contact_email = models.EmailField(
        null=True,
        blank=True,
        verbose_name='contact email',
        help_text='The editable point of contact email')
    point_of_contact_publicly_visible = models.BooleanField(
        null=False,
        default=False,
        verbose_name='is contact visible',
        help_text='Is the point of contact info publicly visible?')
    office_official_name = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name='office official name',
        help_text='The editable office name for this claim.')
    office_address = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name='office address',
        help_text='The editable office address for this claim.')
    office_country_code = models.CharField(
        max_length=2,
        null=True,
        blank=True,
        choices=COUNTRY_CHOICES,
        verbose_name='office country code',
        help_text='The editable office country code for this claim.')
    office_phone_number = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name='office phone number',
        help_text='The editable office phone number for this claim.')
    office_info_publicly_visible = models.BooleanField(
        null=False,
        default=False,
        verbose_name='is office publicly visible',
        help_text='Is the office info publicly visible?')
    parent_company = models.ForeignKey(
        'Contributor',
        related_name='parent_company',
        null=True,
        default=None,
        on_delete=models.PROTECT,
        verbose_name='contributor parent company / supplier group',
        help_text='The contributor parent company / supplier group '
        'of thisfacility claim.')
    parent_company_name = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name='parent company / supplier group',
        help_text='The parent company / supplier group of this '
        'facility claim.')
    sector = postgres.ArrayField(
        models.CharField(max_length=50, null=False, blank=False),
        null=True,
        blank=True,
        help_text='The sector(s) for goods made at the facility',
    )
    origin_source = models.CharField(
        choices=OriginSource.CHOICES,
        null=True,
        max_length=200,
        help_text="The environment value where instance running"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    history = HistoricalRecords()

    default_change_includes = (
        'facility_name_english',
        'facility_name_native_language',
        'facility_address',
        'facility_phone_number',
        'facility_website',
        'facility_minimum_order_quantity',
        'facility_average_lead_time',
        'facility_workers_count',
        'facility_female_workers_percentage',
        'facility_affiliations',
        'facility_certifications',
        'facility_product_types',
        'facility_production_types',
        'facility_type',
        'other_facility_type',
        'facility_description',
        'facility_minimum_order_quantity',
        'facility_average_lead_time',
        'point_of_contact_person_name',
        'point_of_contact_email',
        'office_official_name',
        'office_address',
        'office_country_code',
        'office_phone_number',
        'parent_company',
        'sector',
        'facility_location',
    )

    # A dictionary where the keys are field names and the values are predicate
    # functions that will be passed a FacilityClaim instance and should return
    # a boolean.
    change_conditions = defaultdict(
        lambda: lambda c: True,
        facility_phone_number=(
            lambda c: c.facility_phone_number_publicly_visible),
        facility_website=(
            lambda c: c.facility_website_publicly_visible),
        point_of_contact_person_name=(
            lambda c: c.point_of_contact_publicly_visible),
        point_of_contact_email=(
            lambda c: c.point_of_contact_publicly_visible),
        office_official_name=(
            lambda c: c.office_info_publicly_visible),
        office_address=(
            lambda c: c.office_info_publicly_visible),
        office_country_code=(
            lambda c: c.office_info_publicly_visible),
        office_phone_number=(
            lambda c: c.office_info_publicly_visible),
    )

    # A dictionary where the keys are field_names and the values are functions
    # that will be passed a FacilityClaim and should return a string
    change_value_serializers = defaultdict(
        lambda: lambda v: v,
        parent_company=lambda v: v and v.name,
        facility_affiliations=lambda v: ', '.join(v) if v is not None else '',
        facility_certifications=lambda v: ', '.join(v)
        if v is not None else '',
        facility_product_types=lambda v: ', '.join(v)
        if v is not None else '',
        sector=lambda v: ', '.join(v) if v is not None else '',
        facility_location=lambda v: ', '.join([str(v.x), str(v.y)])
        if v is not None else '',
    )

    def get_changes(self, include=list(default_change_includes)):
        latest = self.history.latest()
        previous = latest.prev_record
        changes = None
        if previous is not None:
            for field in FacilityClaim._meta.fields:
                should_report_change_publicly = \
                    self.change_conditions[field.name](self)
                if field.name in include and should_report_change_publicly:
                    curr_value = self.change_value_serializers[field.name](
                        getattr(self, field.name))
                    prev_value = self.change_value_serializers[field.name](
                        getattr(previous.instance, field.name))
                    if curr_value != prev_value:
                        if changes is None:
                            changes = []
                        changes.append({
                            'name': field.name,
                            'verbose_name': field.verbose_name,
                            'previous': prev_value,
                            'current': curr_value,
                        })
        return changes

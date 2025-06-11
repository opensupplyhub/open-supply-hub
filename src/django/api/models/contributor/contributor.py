import uuid
from simple_history.models import HistoricalRecords
from django.db import models

from ...constants import MatchResponsibility
from ...helpers.helpers import prefix_a_an

from .contributor_manager import ContributorManager


class Contributor(models.Model):
    """
    A participant in or observer of the supply chain that will
    upload facility lists to the registry.
    """
    # These choices must be kept in sync with the identical list kept in the
    # React client's constants file
    OTHER_CONTRIB_TYPE = 'Other'

    CONTRIB_TYPE_CHOICES = (
        ('Academic / Researcher / Journalist / Student',
         'Academic / Researcher / Journalist / Student'),
        ('Auditor / Certification Scheme / Service Provider',
         'Auditor / Certification Scheme / Service Provider'),
        ('Brand / Retailer', 'Brand / Retailer'),
        ('Civil Society Organization', 'Civil Society Organization'),
        ('Facility / Factory / Manufacturing Group / Supplier / Vendor',
         'Facility / Factory / Manufacturing Group / Supplier / Vendor'),
        ('Multi-Stakeholder Initiative', 'Multi-Stakeholder Initiative'),
        ('Union', 'Union'),
        (OTHER_CONTRIB_TYPE, OTHER_CONTRIB_TYPE),
    )

    PLURAL_CONTRIB_TYPE = {
        'Academic / Researcher / Journalist / Student':
        'Academics / Researchers / Journalists / Students',
        'Auditor / Certification Scheme / Service Provider':
        'Auditors / Certification Schemes / Service Providers',
        'Brand / Retailer': 'Brands / Retailers',
        'Civil Society Organization': 'Civil Society Organizations',
        'Facility / Factory / Manufacturing Group / Supplier / Vendor':
        'Facilities / Factories / Manufacturing Groups / Suppliers / Vendors',
        'Multi-Stakeholder Initiative': 'Multi-Stakeholder Initiatives',
        'Union': 'Unions',
        OTHER_CONTRIB_TYPE: 'Others',
    }

    EMBED_LEVEL_CHOICES = (
        (1, 'Embed'),
        (2, 'Embed+'),
        (3, 'Embed Deluxe / Custom Embed'),
    )

    uuid = models.UUIDField(
        null=False,
        default=uuid.uuid4,
        unique=True,
        editable=False,
        help_text='Unique identifier for the contributor.'
    )
    admin = models.OneToOneField(
        'User',
        on_delete=models.PROTECT,
        help_text=('The user account responsible for uploading and '
                   'maintaining facility lists for the contributor'))
    name = models.CharField(
        max_length=200,
        null=False,
        blank=False,
        help_text='The full name of the contributor.')
    description = models.TextField(
        null=False,
        blank=True,
        help_text='A detailed description of the contributor.')
    website = models.URLField(
        null=False,
        blank=True,
        help_text='A URL linking to a web site for the contributor.')
    contrib_type = models.CharField(
        max_length=200,
        null=False,
        blank=False,
        choices=CONTRIB_TYPE_CHOICES,
        help_text='The category to which this contributor belongs.')
    other_contrib_type = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        help_text='Free text field if selected contributor type is other'
    )
    is_verified = models.BooleanField(
        'verified',
        default=False,
        help_text=(
            'Has this contributor has been verified by OS Hub staff.'
        ),
    )
    verification_notes = models.TextField(
        null=False,
        blank=True,
        help_text=(
            'A description of the manual steps taken to verify the '
            'contributor.'
        )
    )
    embed_config = models.OneToOneField(
        'EmbedConfig',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text=('The embedded map configuration for the contributor'))
    embed_level = models.IntegerField(
        null=True,
        blank=True,
        choices=EMBED_LEVEL_CHOICES,
        help_text='The embedded map level that is enabled for the contributor')
    match_responsibility = models.CharField(
        choices=MatchResponsibility.CHOICES,
        default=MatchResponsibility.MODERATOR,
        max_length=12,
        help_text="Who is responsible for moderating this contributor's data"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ContributorManager.as_manager()
    history = HistoricalRecords(
        excluded_fields=['uuid']
    )

    def __str__(self):
        return '{name} ({id})'.format(**self.__dict__)

    @classmethod
    def prefix_with_count(cls, value, count):
        if count != 1:
            contrib_type = cls.PLURAL_CONTRIB_TYPE.get(value, value)
            return f'{count} {contrib_type}'
        if value.lower() == 'other':
            # Special case to avoid returning the awkward "An Other"
            return f'One {value}'
        return prefix_a_an(value)

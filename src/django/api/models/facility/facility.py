import uuid
from itertools import groupby

from api.constants import FacilityClaimStatuses
from api.models.facility.facility_manager import FacilityManager
from simple_history.models import HistoricalRecords

from django.contrib.gis.db import models as gis_models
from django.db import models
from django.db.models import ExpressionWrapper, Q

from countries.lib.countries import COUNTRY_CHOICES
from ...os_id import make_os_id


class Facility(models.Model):
    """
    An official OS Hub facility. Search results are returned from this table.
    """
    class Meta:
        verbose_name_plural = "facilities"

    id = models.CharField(
        max_length=32,
        primary_key=True,
        editable=False,
        db_index=True,
        help_text='The OS ID of a facility.')
    name = models.CharField(
        max_length=200,
        null=False,
        blank=False,
        help_text='The name of the facility.')
    address = models.CharField(
        max_length=200,
        null=False,
        blank=False,
        help_text='The full street address of the facility.')
    country_code = models.CharField(
        max_length=2,
        null=False,
        blank=False,
        choices=COUNTRY_CHOICES,
        help_text='The ISO 3166-1 alpha-2 country code of the facility.')
    location = gis_models.PointField(
        null=False,
        help_text='The lat/lng point location of the facility')
    created_from = models.OneToOneField(
        'FacilityListItem',
        null=False,
        on_delete=models.PROTECT,
        related_name='created_facility',
        help_text=('The original uploaded list item from which this facility '
                   'was created.'))
    is_closed = models.BooleanField(
        null=True,
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    uuid = models.UUIDField(
        null=False,
        default=uuid.uuid4,
        unique=True,
        editable=False,
        help_text='Unique identifier for the facility.'
    )

    @property
    def ids_of_public_contributors(self):
        from .facility_index import FacilityIndex
        return (
            FacilityIndex
            .objects
            .get(id=self.id)
            .contributors
        )

    history = HistoricalRecords()
    objects = FacilityManager()

    def __str__(self):
        return '{name} ({id})'.format(**self.__dict__)

    def save(self, *args, **kwargs):
        if self.id == '':
            new_id = None
            while new_id is None:
                new_id = make_os_id(self.country_code)
                if Facility.objects.filter(id=new_id).exists():
                    new_id = None
            self.id = new_id
        super(Facility, self).save(*args, **kwargs)

    def other_names(self):
        from .facility_list_item import FacilityListItem
        from .facility_match import FacilityMatch
        facility_list_item_matches = [
            FacilityListItem.objects.get(pk=pk)
            for (pk,)
            in (
                self.facilitymatch_set
                .filter(status__in=[
                    FacilityMatch.AUTOMATIC,
                    FacilityMatch.CONFIRMED,
                    FacilityMatch.MERGED
                ])
                .filter(is_active=True)
                .values_list('facility_list_item')
            )
        ]

        return {
            item.name
            for item
            in facility_list_item_matches
            if len(item.name) != 0
            and item.name is not None
            and item.name != self.name
            and item.source.is_active
            and item.source.is_public
        }

    def extended_fields(self, contributor_id=None):
        from .facility_match import FacilityMatch
        active_matches = (
            self
            .facilitymatch_set
            .filter(status__in=[
                FacilityMatch.AUTOMATIC,
                FacilityMatch.CONFIRMED,
                FacilityMatch.MERGED
            ])
            .filter(is_active=True)
            .values_list('facility_list_item')
        )
        active_sources = (
            self
            .facilitylistitem_set
            .filter(source__is_active=True)
            .values_list('id')
        )
        active_items = active_matches.intersection(active_sources)

        from ..extended_field import ExtendedField
        base_qs = ExtendedField.objects.filter(facility=self)

        if contributor_id is not None:
            base_qs = base_qs.filter(contributor_id=contributor_id)

        has_active_claim = Q(
            facility_claim__status=FacilityClaimStatuses.APPROVED
        )
        fields = (
            base_qs
            .annotate(has_active_claim=ExpressionWrapper(
              has_active_claim,
              output_field=models.BooleanField())
            )
            .annotate(is_active=ExpressionWrapper(
                Q(facility_list_item__in=active_items),
                output_field=models.BooleanField())
            )
            .filter(
              Q(has_active_claim=True) | Q(is_active=True)
            )
        )
        return fields

    def other_addresses(self):
        from .facility_list_item import FacilityListItem
        from .facility_match import FacilityMatch

        facility_list_item_matches = [
            FacilityListItem.objects.get(pk=pk)
            for (pk,)
            in (
                self
                .facilitymatch_set
                .filter(status__in=[
                    FacilityMatch.AUTOMATIC,
                    FacilityMatch.CONFIRMED,
                    FacilityMatch.MERGED
                ])
                .filter(is_active=True)
                .values_list('facility_list_item')
            )
        ]

        return {
            match.address
            for match
            in facility_list_item_matches
            if (
                len(match.address) != 0
                and match.address is not None
                and match.address != self.address
                and match.source.is_active
                and match.source.is_public
            )
        }

    def complete_matches(self):
        from .facility_match import FacilityMatch
        return self.facilitymatch_set.filter(
          status__in=[
            FacilityMatch.AUTOMATIC,
            FacilityMatch.CONFIRMED,
            FacilityMatch.MERGED
          ])

    def sources(self, user=None):
        sorted_matches = sorted(
            self.complete_matches()
                .exclude(facility_list_item__source__contributor=None)
                .prefetch_related(
                    'facility_list_item__source__contributor'
                ),
            key=lambda m: m.source.contributor.id
        )

        if user is not None and not user.is_anonymous:
            user_can_see_detail = user.can_view_full_contrib_details
        else:
            user_can_see_detail = True

        sources = []
        anonymous_sources = []
        for contributor, matches in groupby(sorted_matches,
                                            lambda m: m.source.contributor):
            # Convert the groupby result to a list to we can iterate over it
            # multiple times
            matches = list(matches)
            should_display_associations = \
                any([m.should_display_association for m in matches])
            if user_can_see_detail and should_display_associations:
                sources.extend(
                    [m.source
                     for m in matches
                     if m.should_display_association])
            else:
                anonymous_sources.append(contributor.contrib_type)

        from ..contributor.contributor import Contributor
        anonymous_sources = [
            Contributor.prefix_with_count(name, len(list(x)))
            for name, x in groupby(sorted(anonymous_sources))
        ]
        return sources + anonymous_sources

    def get_created_from_matches(self):
        return self.facilitymatch_set.filter(
            facility_list_item=self.created_from
        )

    def get_created_from_match(self):
        return self.get_created_from_matches().first()

    def get_other_matches(self):
        return self.facilitymatch_set.exclude(
            facility_list_item=self.created_from
        ).all().order_by('id')

    def get_approved_claim(self):
        from .facility_claim import FacilityClaim
        return (
            FacilityClaim
            .objects
            .filter(facility=self, status=FacilityClaimStatuses.APPROVED)
            .order_by('-status_change_date')
            .first()
        )

    @staticmethod
    def current_tile_cache_key():
        timestamp = format(
            Facility.objects.latest('updated_at').updated_at,
            'U',
        )
        from ..version import Version
        try:
            tile_version = (
                Version
                .objects
                .get(name='tile_version')
                .version
            )
        except Version.DoesNotExist:
            tile_version = 0

        return f'{timestamp}-{tile_version}'

    @staticmethod
    def update_facility_updated_at_field(facility_id):
        facility = Facility.objects.get(pk=facility_id)
        facility.save(update_fields=['updated_at'])

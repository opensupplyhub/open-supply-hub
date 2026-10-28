from django.contrib.gis.geos import Point
from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from waffle.testutils import override_switch

from api.models import (
    Contributor,
    Facility,
    FacilityList,
    FacilityListItem,
    FacilityMatch,
    Source,
    User,
    ZoneSet,
)
from api.models.extended_field import ExtendedField
from api.models.facility.facility_index import FacilityIndex
from api.models.facility.partner_contributor_filter import (
    apply_partner_contributors_filter,
    apply_partner_fields_or_filter,
)
from api.models.partner_field import PartnerField
from api.models.partner_field_group import PartnerFieldGroup
from api.partner_fields.registry import ZONE_SETS_SWITCH
from api.tests.test_zone_set_provider import EAST, WEST, feature, zone_records


def make_facility(contributor, lon, lat, country_code='IN'):
    """
    Create a Facility (with its list/source/match chain) at lon/lat.

    The database triggers build the matching `FacilityIndex` row, so
    the search filter and the profile spotlight see exactly what they
    would in production, and an `ExtendedField` row can point at the
    facility.
    """
    location = Point(lon, lat, srid=4326)
    facility_list = FacilityList.objects.create(
        header='header', file_name='test', name='Test List'
    )
    source = Source.objects.create(
        facility_list=facility_list,
        source_type=Source.LIST,
        is_active=True,
        is_public=True,
        contributor=contributor,
    )
    list_item = FacilityListItem.objects.create(
        name='Test Facility',
        address='123 Test St',
        country_code=country_code,
        sector=['Apparel'],
        row_index=0,
        geocoded_point=location,
        status=FacilityListItem.CONFIRMED_MATCH,
        source=source,
    )
    facility = Facility.objects.create(
        name='Test Facility',
        address='123 Test St',
        country_code=country_code,
        location=location,
        created_from=list_item,
    )
    FacilityMatch.objects.create(
        status=FacilityMatch.CONFIRMED,
        facility=facility,
        results='',
        facility_list_item=list_item,
    )
    list_item.facility = facility
    list_item.save()
    return facility


@override_switch(ZONE_SETS_SWITCH, active=True)
class ZoneSetPartnerFilterTest(TestCase):
    """Tests for the zone-set branch of the Spotlight Partners search
    filter: a zone-set-backed partner matches the locations its zones
    cover, exactly as the location page resolves them."""

    def setUp(self):
        """Create a zone-set partner, a contributed-field partner, and
        locations inside and outside the zones."""
        self.user = User.objects.create(email='aqueduct@example.com')
        self.contributor = Contributor.objects.create(
            admin=self.user,
            name='WRI Aqueduct',
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )
        self.group = PartnerFieldGroup.objects.create(
            name='Climate', order=1
        )
        self.partner_field = PartnerField.objects.create(
            name='aqueduct_water_stress',
            type=PartnerField.STRING,
            label='Baseline water stress',
            group=self.group,
            active=True,
        )
        self.contributor.partner_fields.add(self.partner_field)
        self.zone_set = ZoneSet.objects.create(
            name='aqueduct_bws',
            description='Baseline water stress bands.',
            partner_field=self.partner_field,
            value_property='bws_label',
        )
        self.zone_set.replace_zones(zone_records(
            feature(WEST, {'bws_label': 'Extremely High'}),
            feature(EAST, {'bws_label': 'Low'}),
        ))

        # Another contributor's facility that happens to sit inside a
        # zone: the search must return it even though the zone-set
        # partner never contributed to it.
        self.other_user = User.objects.create(email='other@example.com')
        self.other_contributor = Contributor.objects.create(
            admin=self.other_user,
            name='Other',
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )
        self.inside_west = make_facility(
            self.other_contributor, 76.9, 28.6
        )
        self.inside_east = make_facility(
            self.other_contributor, 77.3, 28.6
        )
        self.on_edge = make_facility(self.other_contributor, 77.1, 28.9)
        self.outside = make_facility(self.other_contributor, 75.0, 20.0)

    def _add_contributed_field(self, name='aqueduct_notes'):
        """Give the zone-set partner a second, contributed field with
        one ExtendedField row on the outside facility."""
        contributed = PartnerField.objects.create(
            name=name,
            type=PartnerField.STRING,
            label='Notes',
            group=self.group,
            active=True,
        )
        self.contributor.partner_fields.add(contributed)
        ExtendedField.objects.create(
            contributor=self.contributor,
            facility=self.outside,
            field_name=name,
            value={'raw_values': ['note']},
        )
        return contributed

    def _filtered_ids(self, field_names=None):
        """Run the partner-fields filter and return the matched ids."""
        queryset = apply_partner_fields_or_filter(
            FacilityIndex.objects.all(),
            field_names or [self.partner_field.name],
            [self.contributor.id],
        )
        return set(queryset.values_list('id', flat=True))

    def _contributor_filtered_ids(self):
        """Run the Spotlight Partners filter as the search view does."""
        queryset = apply_partner_contributors_filter(
            FacilityIndex.objects.all(), [self.contributor.id]
        )
        return set(queryset.values_list('id', flat=True))

    def test_filter_returns_covered_locations_only(self):
        """Locations inside a zone of the set match; locations outside
        every zone do not."""
        ids = self._filtered_ids()
        self.assertEqual(
            ids,
            {self.inside_west.id, self.inside_east.id, self.on_edge.id},
        )

    def test_filter_uses_covers_like_the_location_page(self):
        """A point exactly on a zone edge matches the search filter,
        as `ZoneSet.resolve_zone` matches it for the location page."""
        index_row = FacilityIndex.objects.get(id=self.on_edge.id)
        self.assertIsNotNone(self.zone_set.resolve_zone(index_row.location))
        self.assertIn(self.on_edge.id, self._filtered_ids())

    def test_filter_via_partner_contributor_matches_zone_locations(self):
        """The contributor-level entry point the search view calls
        resolves the contributor's zone-set field and applies it."""
        ids = self._contributor_filtered_ids()
        self.assertEqual(
            ids,
            {self.inside_west.id, self.inside_east.id, self.on_edge.id},
        )

    def test_zone_set_field_is_not_matched_through_extended_fields(self):
        """A zone-set field name is taken out of the contributed branch,
        so a stray ExtendedField row under that name does not widen
        the results."""
        ExtendedField.objects.create(
            contributor=self.contributor,
            facility=self.outside,
            field_name=self.partner_field.name,
            value={'raw_values': ['stray']},
        )
        self.assertNotIn(self.outside.id, self._filtered_ids())

    @override_switch(ZONE_SETS_SWITCH, active=False)
    def test_filter_matches_nothing_when_switch_is_off(self):
        """With the switch off a zone-set field matches nothing — never
        the full facility list — and the zone tables are not queried."""
        with CaptureQueriesContext(connection) as queries:
            ids = self._filtered_ids()

        self.assertEqual(ids, set())
        self.assertFalse(any(
            'api_zoneset' in query['sql'] or 'api_zone"' in query['sql']
            for query in queries.captured_queries
        ))

    def test_filter_matches_nothing_when_zone_set_is_inactive(self):
        """A retired zone set matches nothing, never everything."""
        self.zone_set.active = False
        self.zone_set.save()
        self.assertEqual(self._filtered_ids(), set())
        self.assertEqual(self._contributor_filtered_ids(), set())

    def test_zone_set_and_contributed_fields_are_unioned(self):
        """A partner holding a zone-set field and a contributed field
        returns the covered locations plus the contributed ones."""
        self._add_contributed_field()
        ids = self._contributor_filtered_ids()
        self.assertEqual(
            ids,
            {
                self.inside_west.id,
                self.inside_east.id,
                self.on_edge.id,
                self.outside.id,
            },
        )

    def test_zone_set_is_unioned_with_hard_wired_fields(self):
        """Zone sets OR with the hard-wired system fields, as every
        other branch of the filter does, leaving those unchanged."""
        us_facility = make_facility(
            self.other_contributor, -100.0, 40.0, country_code='US'
        )

        ids = self._filtered_ids(
            [self.partner_field.name, 'mit_living_wage']
        )
        self.assertEqual(
            ids,
            {
                self.inside_west.id,
                self.inside_east.id,
                self.on_edge.id,
                us_facility.id,
            },
        )

    def test_corrected_coordinates_match_without_reindex(self):
        """A location whose coordinates are corrected to fall inside a
        zone appears on the next search; nothing is precomputed."""
        self.assertNotIn(self.outside.id, self._filtered_ids())
        self.outside.location = Point(77.0, 28.5, srid=4326)
        self.outside.save()
        self.assertIn(self.outside.id, self._filtered_ids())

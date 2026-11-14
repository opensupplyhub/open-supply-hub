from django.contrib.admin.widgets import FilteredSelectMultiple
from django.db.models import Q
from django.test import SimpleTestCase, TestCase
from waffle.testutils import override_switch

from api.helpers.location_filters import (
    FILTERABLE_FIELDS,
    MAX_VALUES_PER_FILTER,
    build_filters_q,
    clean_filters,
    has_filters,
)
from api.models import (
    Contributor,
    PartnerField,
    Polygon,
    Sector,
    User,
    ZoneSet,
)
from api.models.facility.facility_index import FacilityIndex
from api.models.facility.partner_contributor_filter import (
    apply_partner_fields_or_filter,
)
from api.models.partner_field_group import PartnerFieldGroup
from api.models.zone_set_admin import ZoneSetForm
from api.partner_fields.registry import ZONE_SETS_SWITCH
from api.partner_fields.zone_set_provider import (
    ZoneSetProvider,
    build_zone_sets_covered_q,
)
from api.tests.test_zone_set_provider import (
    EAST,
    WEST,
    feature,
    make_facility,
    zone_pieces,
)
from api.tests.zone_fixtures import upload

FORM_DATA = {
    'name': 'mining_reports',
    'description': 'Mining reports for tests.',
    'value_property': 'label',
    'active': True,
}


class LocationFiltersHelperTest(SimpleTestCase):
    """Tests for validating and building the shared location filters."""

    def test_no_filters_means_empty(self):
        """None and an empty object both mean "no filters"."""
        self.assertEqual(clean_filters(None), {})
        self.assertEqual(clean_filters({}), {})
        self.assertIsNone(build_filters_q(None))
        self.assertIsNone(build_filters_q({}))

    def test_single_string_becomes_a_one_item_list(self):
        self.assertEqual(
            clean_filters({'sector': 'Mining'}), {'sector': ['Mining']}
        )

    def test_values_are_trimmed_and_countries_upper_cased(self):
        self.assertEqual(
            clean_filters({'country': [' kh '], 'sector': [' Mining ']}),
            {'country': ['KH'], 'sector': ['Mining']},
        )

    def test_product_types_are_lower_cased_and_deduplicated(self):
        """The index stores product types in lower case, so a filter
        value with capitals could never match. 'Sugar Cane' and
        'sugar cane' are therefore the same entry."""
        self.assertEqual(
            clean_filters(
                {'product_type': ['Sugar Cane', 'sugar cane', 'SUGARCANE']}
            ),
            {'product_type': ['sugar cane', 'sugarcane']},
        )

    def test_other_fields_keep_their_capitals(self):
        """Sectors and the like are stored as typed, so they must match
        exactly and are not lower-cased."""
        self.assertEqual(
            clean_filters({'sector': ['Home Textiles']}),
            {'sector': ['Home Textiles']},
        )

    def test_only_none_and_empty_dict_mean_no_filters(self):
        """Anything else, even something empty, is a filter setting that
        has to be valid, so it can never be read as "no restriction"."""
        self.assertFalse(has_filters(None))
        self.assertFalse(has_filters({}))
        for value in ([], '', 0, False, ['x'], 'text', {'sector': ['a']}):
            self.assertTrue(has_filters(value), repr(value))

    def test_empty_but_wrong_type_values_are_refused_not_ignored(self):
        """An empty list, empty text or zero must not quietly mean "no
        filters": that would show a dataset on every location."""
        for value in ([], '', 0, False):
            with self.assertRaises(ValueError, msg=repr(value)):
                clean_filters(value)
            with self.assertRaises(ValueError, msg=repr(value)):
                build_filters_q(value)

    def test_a_key_may_list_at_most_the_limit(self):
        at_limit = [f'p{i}' for i in range(MAX_VALUES_PER_FILTER)]
        self.assertEqual(
            len(clean_filters({'sector': at_limit})['sector']),
            MAX_VALUES_PER_FILTER,
        )
        with self.assertRaisesMessage(ValueError, 'the limit is'):
            clean_filters({'sector': at_limit + ['one more']})

    def test_unknown_key_is_refused(self):
        """A typo must fail loudly, never filter nothing."""
        with self.assertRaisesMessage(ValueError, 'Unknown filter field'):
            clean_filters({'sectr': ['Mining']})

    def test_empty_list_is_refused(self):
        """An empty list would match no location, so the field would
        silently never show."""
        with self.assertRaisesMessage(ValueError, 'at least one value'):
            clean_filters({'sector': []})

    def test_blank_and_non_text_values_are_refused(self):
        with self.assertRaisesMessage(ValueError, 'non-blank text'):
            clean_filters({'sector': ['Mining', '  ']})
        with self.assertRaisesMessage(ValueError, 'non-blank text'):
            clean_filters({'sector': [3]})

    def test_non_object_is_refused(self):
        with self.assertRaisesMessage(ValueError, 'JSON object'):
            clean_filters(['Mining'])

    def test_build_q_ands_the_keys(self):
        """Values within a key are alternatives; keys are all required,
        so the condition is an AND of one lookup per key."""
        condition = build_filters_q(
            {'sector': ['Mining'], 'country': ['pe']}
        )
        self.assertEqual(
            condition,
            Q(sector__overlap=['Mining']) & Q(country_code__in=['PE']),
        )

    def test_sector_and_product_type_are_anded(self):
        """Sector and product type are separate conditions and a
        location must satisfy both; product values are lower-cased."""
        condition = build_filters_q(
            {'sector': ['Mining'], 'product_type': ['Sugar Cane', 'sugar']}
        )
        self.assertEqual(
            condition,
            Q(sector__overlap=['Mining'])
            & Q(product_type__overlap=['sugar cane', 'sugar']),
        )
        self.assertEqual(condition.connector, Q.AND)

    def test_build_q_refuses_an_unknown_key(self):
        """A stored value that was never cleaned must not widen a
        search."""
        with self.assertRaises(ValueError):
            build_filters_q({'nope': ['x']})

    def test_polygons_share_the_same_allowlist(self):
        """Zone sets and polygons must agree on what a filter means."""
        self.assertIs(Polygon.FILTERABLE_FIELDS, FILTERABLE_FIELDS)


@override_switch(ZONE_SETS_SWITCH, active=True)
class ZoneSetFiltersTest(TestCase):
    """Tests for a zone set limited to locations matching its filters,
    on the provider, the shared search condition and the admin form."""

    def setUp(self):
        """A string zone set over two bands, a partner holding its
        field, and in-zone facilities with different sectors."""
        self.user = User.objects.create(email='fwm@example.com')
        self.contributor = Contributor.objects.create(
            admin=self.user,
            name='Fair Work Monitor',
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )
        self.group = PartnerFieldGroup.objects.create(
            name='Labor', order=1
        )
        self.partner_field = PartnerField.objects.create(
            name='fwm_mining',
            type=PartnerField.STRING,
            label='Fair Work Monitor: mining',
            group=self.group,
            active=True,
        )
        self.contributor.partner_fields.add(self.partner_field)
        self.zone_set = ZoneSet.objects.create(
            name='fwm_mining',
            description='FWM mining reports.',
            partner_field=self.partner_field,
            value_property='label',
        )
        self.zone_set.replace_zones(zone_pieces(
            feature(WEST, {'label': 'West report'}),
            feature(EAST, {'label': 'East report'}),
            value_property='label',
        ))
        self.provider = ZoneSetProvider(self.zone_set)

        self.mine = self._facility(76.9, 28.6, ['Mining'])
        self.textile = self._facility(76.95, 28.6, ['Apparel'])
        self.both = self._facility(77.3, 28.6, ['Apparel', 'Mining'])
        self.outside = self._facility(75.0, 20.0, ['Mining'])

    def _facility(self, lon, lat, sector, country_code='IN'):
        """Create a facility whose indexed sector is the given list.

        The index row is built by database triggers from the list
        item, so the sector is set on the row afterwards."""
        facility = make_facility(self.contributor, lon, lat, country_code)
        FacilityIndex.objects.filter(id=facility.id).update(sector=sector)
        return facility

    def _tagged(self, lon, lat, sector, products):
        """A facility with the given sectors AND product types, as the
        search index would hold them (product types in lower case)."""
        facility = self._facility(lon, lat, sector)
        FacilityIndex.objects.filter(id=facility.id).update(
            product_type=[p.lower() for p in products]
        )
        return facility

    def _search_ids(self, zone_sets=None):
        """The facility ids the shared search condition returns."""
        zone_sets = zone_sets or [self.zone_set]
        return set(
            FacilityIndex.objects
            .filter(build_zone_sets_covered_q(zone_sets))
            .values_list('id', flat=True)
        )

    # --- no filters: behaviour is unchanged -----------------------

    def test_without_filters_every_location_in_a_zone_matches(self):
        self.assertEqual(self.zone_set.filters, {})
        self.assertIsNotNone(self.provider.fetch_data(self.textile))
        self.assertEqual(
            self._search_ids(),
            {self.mine.id, self.textile.id, self.both.id},
        )

    # --- location page and v1 endpoint ---------------------------

    def test_provider_serves_only_matching_locations(self):
        self.zone_set.filters = {'sector': ['Mining']}
        self.zone_set.save()

        self.assertEqual(
            self.provider.fetch_data(self.mine)['value'],
            {'raw_value': 'West report'},
        )
        self.assertIsNone(self.provider.fetch_data(self.textile))

    def test_product_filter_ignores_capitals(self):
        """The index holds 'sugar cane' in lower case. A filter written
        'Sugar Cane' must still match it, on the location page and in
        search, because product types are lower-cased when cleaned."""
        FacilityIndex.objects.filter(id=self.textile.id).update(
            product_type=['sugar cane']
        )
        self.zone_set.filters = {'product_type': ['Sugar Cane']}
        self.zone_set.save()

        self.assertIsNotNone(self.provider.fetch_data(self.textile))
        self.assertIsNone(self.provider.fetch_data(self.mine))
        self.assertEqual(self._search_ids(), {self.textile.id})

    def test_sugar_does_not_match_sugarcane(self):
        """Only capitals are ignored: 'sugar' is a different product
        from 'sugarcane' and 'sugar cane'."""
        FacilityIndex.objects.filter(id=self.textile.id).update(
            product_type=['sugarcane']
        )
        self.zone_set.filters = {'product_type': ['sugar']}
        self.zone_set.save()
        self.assertIsNone(self.provider.fetch_data(self.textile))

    def test_a_location_in_two_sectors_matches_either(self):
        """Sector is an array: any shared value is enough."""
        self.zone_set.filters = {'sector': ['Mining']}
        self.zone_set.save()
        self.assertEqual(
            self.provider.fetch_data(self.both)['value'],
            {'raw_value': 'East report'},
        )

    def test_values_in_one_key_are_alternatives(self):
        self.zone_set.filters = {'sector': ['Apparel', 'Footwear']}
        self.zone_set.save()
        self.assertIsNone(self.provider.fetch_data(self.mine))
        self.assertIsNotNone(self.provider.fetch_data(self.textile))

    # --- sector AND product type ----------------------------------

    def _combined_set(self):
        """Filter the set to Mining AND (sugar or sugarcane), and make
        five locations that each hit a different part of that rule."""
        self.zone_set.filters = {
            'sector': ['Mining'],
            'product_type': ['sugar', 'sugarcane'],
        }
        self.zone_set.save()
        return {
            'both': self._tagged(76.90, 28.60, ['Mining'], ['sugar']),
            'sector_only': self._tagged(76.91, 28.61, ['Mining'], []),
            'product_only': self._tagged(
                76.92, 28.62, ['Apparel'], ['sugarcane']
            ),
            'wrong_product': self._tagged(
                76.93, 28.63, ['Mining'], ['palm oil']
            ),
            'one_of_two_products': self._tagged(
                77.30, 28.60, ['Mining'], ['copper', 'Sugarcane']
            ),
        }

    def test_sector_and_product_must_both_match_on_the_page(self):
        """A location shows the data only when it has the sector AND at
        least one listed product. Either alone is not enough."""
        facilities = self._combined_set()

        shown = {
            name for name, facility in facilities.items()
            if self.provider.fetch_data(facility) is not None
        }

        self.assertEqual(shown, {'both', 'one_of_two_products'})

    def test_sector_and_product_must_both_match_in_search(self):
        facilities = self._combined_set()

        found = self._search_ids()

        self.assertIn(facilities['both'].id, found)
        self.assertIn(facilities['one_of_two_products'].id, found)
        for name in ('sector_only', 'product_only', 'wrong_product'):
            self.assertNotIn(facilities[name].id, found, name)

    def test_page_and_search_agree_for_sector_and_product(self):
        """The two surfaces answer from one rule, so the locations the
        page serves are the locations search returns."""
        facilities = self._combined_set()
        served = {
            facility.id for facility in facilities.values()
            if self.provider.fetch_data(facility) is not None
        }
        everything = set(facilities[n].id for n in facilities) | {
            self.mine.id, self.textile.id, self.both.id,
        }
        self.assertEqual(served, self._search_ids() & everything)

    def test_adding_a_product_filter_narrows_a_sector_filter(self):
        """AND, not OR: setting the product box on top of a sector
        filter can only remove locations, never add any."""
        facilities = self._combined_set()
        self.zone_set.filters = {'sector': ['Mining']}
        self.zone_set.save()
        sector_only = self._search_ids()

        self.zone_set.filters = {
            'sector': ['Mining'], 'product_type': ['sugar', 'sugarcane'],
        }
        self.zone_set.save()
        combined = self._search_ids()

        self.assertTrue(combined < sector_only, (combined, sector_only))
        self.assertIn(facilities['sector_only'].id, sector_only)
        self.assertNotIn(facilities['sector_only'].id, combined)

    def test_partner_search_filter_ands_sector_and_product(self):
        """The Spotlight Partners filter uses the same combined rule."""
        facilities = self._combined_set()
        ids = set(
            apply_partner_fields_or_filter(
                FacilityIndex.objects.all(),
                ['fwm_mining'],
                [self.contributor.id],
            ).values_list('id', flat=True)
        )
        self.assertEqual(
            ids,
            {facilities['both'].id, facilities['one_of_two_products'].id},
        )

    def test_sector_and_product_work_for_a_facility_index_row(self):
        """The location page passes a FacilityIndex, the v1 endpoint a
        Facility; the combined rule is the same for both."""
        facilities = self._combined_set()
        for name, expected in (('both', True), ('sector_only', False),
                               ('product_only', False)):
            row = FacilityIndex.objects.get(id=facilities[name].id)
            self.assertEqual(
                self.provider.fetch_data(row) is not None, expected, name
            )

    def test_keys_must_all_match(self):
        self.zone_set.filters = {'sector': ['Mining'], 'country': ['PE']}
        self.zone_set.save()
        self.assertIsNone(self.provider.fetch_data(self.mine))
        self.zone_set.filters = {'sector': ['Mining'], 'country': ['in']}
        self.zone_set.save()
        self.assertIsNotNone(self.provider.fetch_data(self.mine))

    def test_filters_work_for_a_facility_and_for_a_facility_index(self):
        """The location page passes a FacilityIndex and the v1 endpoint
        a Facility; both must be judged the same."""
        self.zone_set.filters = {'sector': ['Mining']}
        self.zone_set.save()
        index_row = FacilityIndex.objects.get(id=self.textile.id)
        self.assertIsNone(self.provider.fetch_data(index_row))
        index_row = FacilityIndex.objects.get(id=self.mine.id)
        self.assertIsNotNone(self.provider.fetch_data(index_row))

    def test_filters_take_effect_without_a_reupload(self):
        """Filters are applied to the location when it is served, so
        changing them needs no new file."""
        self.assertIsNotNone(self.provider.fetch_data(self.textile))
        self.zone_set.filters = {'sector': ['Mining']}
        self.zone_set.save()
        self.assertIsNone(self.provider.fetch_data(self.textile))

    def test_outside_every_zone_skips_the_filter_lookup(self):
        """A location outside every zone is the common case, so it must
        not pay for the filter query."""
        self.zone_set.filters = {'sector': ['Mining']}
        self.zone_set.save()
        with self.assertNumQueries(1):
            self.assertIsNone(self.provider.fetch_data(self.outside))

    # --- search and spotlight -------------------------------------

    def test_search_condition_applies_the_filters(self):
        self.zone_set.filters = {'sector': ['Mining']}
        self.zone_set.save()
        self.assertEqual(
            self._search_ids(), {self.mine.id, self.both.id}
        )

    def test_search_and_location_page_agree(self):
        """The two surfaces answer from the same rule, so the set of
        locations the page serves is the set search returns."""
        self.zone_set.filters = {'sector': ['Apparel']}
        self.zone_set.save()
        served = {
            facility.id
            for facility in (
                self.mine, self.textile, self.both, self.outside
            )
            if self.provider.fetch_data(facility) is not None
        }
        self.assertEqual(served, self._search_ids())

    def test_partner_search_filter_applies_the_filters(self):
        """The Spotlight Partners filter goes through the same
        condition."""
        self.zone_set.filters = {'sector': ['Mining']}
        self.zone_set.save()
        ids = set(
            apply_partner_fields_or_filter(
                FacilityIndex.objects.all(),
                ['fwm_mining'],
                [self.contributor.id],
            ).values_list('id', flat=True)
        )
        self.assertEqual(ids, {self.mine.id, self.both.id})

    def test_filtered_and_unfiltered_sets_combine_with_or(self):
        """A filtered set only narrows itself; an unfiltered set in the
        same search still covers everything inside its zones."""
        other_field = PartnerField.objects.create(
            name='fwm_textile',
            type=PartnerField.STRING,
            label='Fair Work Monitor: textile',
            group=self.group,
            active=True,
        )
        other = ZoneSet.objects.create(
            name='fwm_textile',
            description='FWM textile reports.',
            partner_field=other_field,
            value_property='label',
        )
        # Replacing zones recomputes search membership once the
        # transaction commits; a TestCase never commits, so run that
        # step explicitly or the facilities already in the table would
        # never be indexed under the new set.
        with self.captureOnCommitCallbacks(execute=True):
            other.replace_zones(zone_pieces(
                feature(WEST, {'label': 'West textile'}),
                value_property='label',
            ))
        self.zone_set.filters = {'sector': ['Mining']}
        self.zone_set.save()

        ids = self._search_ids([self.zone_set, other])

        # `textile` is in the west band, so only the unfiltered set
        # covers it; `both` is in the east band, so only the filtered
        # set does.
        self.assertEqual(
            ids, {self.mine.id, self.textile.id, self.both.id}
        )

    # --- unusable stored filters fail closed ----------------------

    def test_unusable_stored_filters_match_nothing_on_the_page(self):
        """A bad value can only get in outside the admin form. It must
        not break the location page (no error), and must not widen what
        is shown: the set matches nothing, and the problem is logged."""
        self.zone_set.filters = {'sectr': ['Mining']}
        self.zone_set.save()

        with self.assertLogs('api.models.zone_set', level='ERROR') as logs:
            data = self.provider.fetch_data(self.mine)

        self.assertIsNone(data)
        self.assertIn('cannot be used', logs.output[0])
        self.assertIn(self.zone_set.name, logs.output[0])

    def test_unusable_stored_filters_match_nothing_in_search(self):
        """Search returns no location for the bad set instead of
        raising, and a good set searched alongside it is unaffected."""
        other_field = PartnerField.objects.create(
            name='fwm_other', type=PartnerField.STRING, label='Other',
            group=self.group, active=True,
        )
        other = ZoneSet.objects.create(
            name='fwm_other', description='Unfiltered neighbour.',
            partner_field=other_field, value_property='label',
        )
        with self.captureOnCommitCallbacks(execute=True):
            other.replace_zones(zone_pieces(
                feature(WEST, {'label': 'West other'}),
                value_property='label',
            ))
        self.zone_set.filters = ['not', 'a', 'dict']
        self.zone_set.save()

        with self.assertLogs('api.models.zone_set', level='ERROR'):
            both_sets = self._search_ids([self.zone_set, other])
            bad_alone = self._search_ids([self.zone_set])

        self.assertEqual(bad_alone, set())
        # Only the unfiltered neighbour's west band contributes.
        self.assertEqual(both_sets, {self.mine.id, self.textile.id})

    def test_empty_but_wrong_type_stored_filters_are_not_no_filters(self):
        """[], '' and 0 are not "no filters". They match nothing rather
        than showing the dataset on every location in its zones."""
        for bad in ([], '', 0):
            self.zone_set.filters = bad
            self.zone_set.save()
            with self.assertLogs('api.models.zone_set', level='ERROR'):
                self.assertIsNone(
                    self.provider.fetch_data(self.textile), repr(bad)
                )
                self.assertEqual(self._search_ids(), set(), repr(bad))

    def test_empty_dict_and_none_still_mean_no_filters(self):
        for fine in ({}, None):
            self.zone_set.filters = fine
            self.assertIsNone(self.zone_set.filters_condition(), repr(fine))
            self.assertTrue(self.zone_set.passes_filters(self.textile))

    # --- admin form -----------------------------------------------

    def _form(self, **filter_data):
        """A create form for a string set with the given filter inputs
        (`filter_sectors`, `filter_product_types`, `filter_other`)."""
        return ZoneSetForm(
            data={**FORM_DATA, **filter_data},
            files={'geojson_file': upload(
                feature(
                    [[[0, 0], [0, 10], [5, 10], [5, 0], [0, 0]]],
                    {'label': 'High'},
                ),
            )},
        )

    def _edit_form(self, **filter_data):
        """An edit form for the saved set, without a new file."""
        return ZoneSetForm(
            data={
                'name': 'fwm_mining',
                'description': 'FWM mining reports.',
                'partner_field': self.partner_field.pk,
                'value_property': 'label',
                'active': True,
                **filter_data,
            },
            instance=self.zone_set,
        )

    def test_form_with_no_filters_saves_an_empty_setting(self):
        form = self._form()
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.instance.filters, {})

    def test_form_offers_every_os_hub_sector_as_choices(self):
        """The picker lists the whole sector table (OS Hub's default
        sectors), alphabetically, so any of them can be chosen."""
        Sector.objects.get_or_create(name='Mining')
        Sector.objects.get_or_create(name='Apparel')
        form = ZoneSetForm()
        offered = [name for name, _ in form.fields['filter_sectors'].choices]
        self.assertEqual(
            offered,
            sorted(Sector.objects.values_list('name', flat=True)),
        )
        self.assertIn('Mining', offered)
        self.assertIn('Apparel', offered)

    def test_sector_picker_is_the_admin_multi_select(self):
        """A searchable multi-select, not a plain list box."""
        widget = ZoneSetForm().fields['filter_sectors'].widget
        self.assertIsInstance(widget, FilteredSelectMultiple)

    def test_no_sector_chosen_means_no_sector_filter(self):
        form = self._form(filter_sectors=[])
        self.assertTrue(form.is_valid(), form.errors)
        self.assertNotIn('sector', form.instance.filters)

    def test_form_takes_several_sectors(self):
        Sector.objects.get_or_create(name='Mining')
        Sector.objects.get_or_create(name='Agriculture')
        form = self._form(filter_sectors=['Mining', 'Agriculture'])
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(
            form.instance.filters,
            {'sector': ['Mining', 'Agriculture']},
        )

    def test_form_refuses_a_sector_not_in_the_taxonomy(self):
        form = self._form(filter_sectors=['Not a sector'])
        self.assertFalse(form.is_valid())
        self.assertIn('filter_sectors', form.errors)

    def test_form_takes_several_products_one_per_line(self):
        """Add sugar, then sugarcane: both end up in the filter."""
        form = self._form(
            filter_product_types='sugar\n\n  sugarcane \nsugar\n'
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(
            form.instance.filters,
            {'product_type': ['sugar', 'sugarcane']},
        )

    def test_product_box_refuses_commas_with_a_clear_message(self):
        """Several products on one line (comma or semicolon separated)
        is refused, not guessed at: matching is exact, so splitting or
        keeping the line would both filter on the wrong text."""
        for text in ('sugar, sugarcane', 'sugar;sugarcane'):
            form = self._form(filter_product_types=text)
            self.assertFalse(form.is_valid(), text)
            message = str(form.errors['filter_product_types'])
            self.assertIn('own line', message)

    def test_product_box_keeps_spaces_and_ignores_capitals(self):
        """Spaces inside a name matter; capitals do not, so these two
        lines are one entry."""
        form = self._form(filter_product_types='Sugar Cane\nsugar cane')
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(
            form.instance.filters, {'product_type': ['sugar cane']}
        )

    def test_product_box_spacing_and_hyphens_are_different_products(self):
        form = self._form(
            filter_product_types='sugarcane\nsugar cane\nsugar-cane'
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(
            form.instance.filters,
            {'product_type': ['sugarcane', 'sugar cane', 'sugar-cane']},
        )

    def test_sector_and_product_boxes_are_combined_with_and(self):
        """Both boxes feed one filters setting, which the rule treats as
        AND across keys: a location needs a chosen sector and a listed
        product."""
        Sector.objects.get_or_create(name='Mining')
        form = self._form(
            filter_sectors=['Mining'],
            filter_product_types='sugar\nsugarcane',
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(
            form.instance.filters,
            {'sector': ['Mining'], 'product_type': ['sugar', 'sugarcane']},
        )
        condition = build_filters_q(form.instance.filters)
        self.assertEqual(condition.connector, Q.AND)

    def test_both_boxes_say_they_combine_with_and(self):
        """Staff are told on the form that the boxes combine with AND."""
        form = ZoneSetForm()
        sector_help = form.fields['filter_sectors'].help_text
        product_help = form.fields['filter_product_types'].help_text
        self.assertIn('ALL of the filled boxes', sector_help)
        self.assertIn('AND', sector_help)
        self.assertIn('must match both', product_help)

    def test_product_box_refuses_too_many_values(self):
        """One mistaken paste must not become an enormous filter."""
        lines = '\n'.join(f'product {i}' for i in range(
            MAX_VALUES_PER_FILTER + 1
        ))
        form = self._form(filter_product_types=lines)
        self.assertFalse(form.is_valid())
        self.assertIn('the limit is', str(form.non_field_errors()))

    def test_product_box_accepts_exactly_the_limit(self):
        lines = '\n'.join(f'product {i}' for i in range(
            MAX_VALUES_PER_FILTER
        ))
        form = self._form(filter_product_types=lines)
        self.assertTrue(form.is_valid(), form.errors)

    def test_filter_boxes_have_a_length_limit(self):
        form = self._form(filter_product_types='a' * 10001)
        self.assertFalse(form.is_valid())
        self.assertIn('filter_product_types', form.errors)
        form = self._form(filter_other='x' * 5001)
        self.assertFalse(form.is_valid())
        self.assertIn('filter_other', form.errors)

    def test_product_box_shows_the_format_to_staff(self):
        """The format has to be stated on the form itself."""
        field = ZoneSetForm().fields['filter_product_types']
        self.assertIn('ONE product type per line', field.help_text)
        self.assertIn('Do not use commas', field.help_text)
        self.assertIn('Capital letters do not matter', field.help_text)
        self.assertIn('placeholder', field.widget.attrs)

    def test_form_combines_sectors_products_and_other_filters(self):
        Sector.objects.get_or_create(name='Agriculture')
        form = self._form(
            filter_sectors=['Agriculture'],
            filter_product_types='sugarcane',
            filter_other='{"country": ["bo"]}',
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(
            form.instance.filters,
            {
                'country': ['BO'],
                'sector': ['Agriculture'],
                'product_type': ['sugarcane'],
            },
        )

    def test_other_filters_must_be_valid_json(self):
        form = self._form(filter_other='{country: KH')
        self.assertFalse(form.is_valid())
        self.assertIn('Not valid JSON', str(form.errors['filter_other']))

    def test_other_filters_refuse_keys_with_their_own_box(self):
        form = self._form(filter_other='{"sector": ["Mining"]}')
        self.assertFalse(form.is_valid())
        self.assertIn('cannot be set here', str(form.errors['filter_other']))

    def test_other_filters_refuse_an_unknown_key(self):
        form = self._form(filter_other='{"countri": ["KH"]}')
        self.assertFalse(form.is_valid())

    def test_other_filters_refuse_an_empty_list(self):
        """An empty list would match no location, so the field would
        silently never show."""
        form = self._form(filter_other='{"country": []}')
        self.assertFalse(form.is_valid())
        self.assertIn('at least one value', str(form.non_field_errors()))

    def test_edit_form_shows_the_saved_filters(self):
        Sector.objects.get_or_create(name='Mining')
        self.zone_set.filters = {
            'sector': ['Mining'],
            'product_type': ['sugar', 'sugarcane'],
            'country': ['PE'],
        }
        self.zone_set.save()

        form = ZoneSetForm(instance=ZoneSet.objects.get(pk=self.zone_set.pk))

        self.assertEqual(form.initial['filter_sectors'], ['Mining'])
        self.assertEqual(
            form.initial['filter_product_types'], 'sugar\nsugarcane'
        )
        self.assertEqual(form.initial['filter_other'], '{"country": ["PE"]}')

    def test_edit_form_keeps_a_sector_missing_from_the_taxonomy(self):
        """Opening and saving a set must not silently drop a sector the
        taxonomy no longer lists."""
        self.zone_set.filters = {'sector': ['Retired sector']}
        self.zone_set.save()
        form = ZoneSetForm(instance=ZoneSet.objects.get(pk=self.zone_set.pk))
        offered = [name for name, _ in form.fields['filter_sectors'].choices]
        self.assertIn('Retired sector', offered)

    def test_editing_filters_later_keeps_the_zones(self):
        """Filters are applied to locations at serve time, so changing
        them on a set that already has zones needs no new file."""
        Sector.objects.get_or_create(name='Mining')
        form = self._edit_form(filter_sectors=['Mining'])
        self.assertTrue(form.is_valid(), form.errors)
        self.assertIsNone(form.parsed_zones)
        self.assertEqual(form.instance.filters, {'sector': ['Mining']})

    def test_editing_can_add_more_filters_and_then_clear_them(self):
        Sector.objects.get_or_create(name='Mining')
        self.zone_set.filters = {'sector': ['Mining']}
        self.zone_set.save()

        add = self._edit_form(
            filter_sectors=['Mining'],
            filter_product_types='sugar\nsugarcane',
        )
        self.assertTrue(add.is_valid(), add.errors)
        self.assertEqual(
            add.instance.filters,
            {'sector': ['Mining'], 'product_type': ['sugar', 'sugarcane']},
        )

        clear = self._edit_form()
        self.assertTrue(clear.is_valid(), clear.errors)
        self.assertEqual(clear.instance.filters, {})

    def test_editing_other_things_does_not_disturb_the_filters(self):
        """Saving the saved values back leaves the filters as they were
        and still allows the rest of the set to be edited."""
        Sector.objects.get_or_create(name='Mining')
        self.zone_set.filters = {
            'sector': ['Mining'], 'product_type': ['sugar'],
        }
        self.zone_set.save()
        form = self._edit_form(
            description='Reworded description.',
            filter_sectors=['Mining'],
            filter_product_types='sugar',
        )
        self.assertTrue(form.is_valid(), form.errors)
        saved = form.save()
        saved.refresh_from_db()
        self.assertEqual(saved.description, 'Reworded description.')
        self.assertEqual(
            saved.filters, {'sector': ['Mining'], 'product_type': ['sugar']}
        )

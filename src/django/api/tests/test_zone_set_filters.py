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

    def test_only_none_and_empty_dict_mean_no_filters(self):
        """Anything else, even something empty, is a filter setting that
        has to be valid, so it can never be read as "no restriction"."""
        self.assertFalse(has_filters(None))
        self.assertFalse(has_filters({}))
        for value in ([], '', 0, False, ['x'], 'text', {'sector': ['a']}):
            self.assertTrue(has_filters(value), repr(value))
        for none_like in (None, {}):
            self.assertEqual(clean_filters(none_like), {})
            self.assertIsNone(build_filters_q(none_like))

    def test_values_are_normalised(self):
        """A single string becomes a one-item list, values are trimmed,
        countries are upper-cased, and sectors keep their capitals (they
        are stored as typed, so they must match exactly)."""
        self.assertEqual(
            clean_filters({'sector': 'Mining'}), {'sector': ['Mining']}
        )
        self.assertEqual(
            clean_filters({'country': [' kh '], 'sector': [' Mining ']}),
            {'country': ['KH'], 'sector': ['Mining']},
        )
        self.assertEqual(
            clean_filters({'sector': ['Home Textiles']}),
            {'sector': ['Home Textiles']},
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

    def test_unusable_settings_are_refused_with_a_clear_message(self):
        """Anything that would quietly match nothing is refused: a typo
        must fail loudly, an empty list would make the field silently
        never show, and blank or non-text values make no sense."""
        cases = (
            ({'sectr': ['Mining']}, 'Unknown filter field'),
            ({'sector': []}, 'at least one value'),
            ({'sector': ['Mining', '  ']}, 'non-blank text'),
            ({'sector': [3]}, 'non-blank text'),
            (['Mining'], 'JSON object'),
        )
        for setting, message in cases:
            with self.subTest(setting=setting):
                with self.assertRaisesMessage(ValueError, message):
                    clean_filters(setting)
        # A stored value that was never cleaned must not widen a search.
        with self.assertRaises(ValueError):
            build_filters_q({'nope': ['x']})

    def test_build_q_ands_the_keys(self):
        """Values within a key are alternatives; keys are all required,
        so the condition is an AND of one lookup per key. Sector and
        product type are separate conditions (product lower-cased)."""
        self.assertEqual(
            build_filters_q({'sector': ['Mining'], 'country': ['pe']}),
            Q(sector__overlap=['Mining']) & Q(country_code__in=['PE']),
        )
        condition = build_filters_q(
            {'sector': ['Mining'], 'product_type': ['Sugar Cane', 'sugar']}
        )
        self.assertEqual(
            condition,
            Q(sector__overlap=['Mining'])
            & Q(product_type__overlap=['sugar cane', 'sugar']),
        )
        self.assertEqual(condition.connector, Q.AND)

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

    def _set_filters(self, filters):
        """Save filters on the zone set directly, as a stored value."""
        self.zone_set.filters = filters
        self.zone_set.save()

    def _search_ids(self, zone_sets=None):
        """The facility ids the shared search condition returns."""
        zone_sets = zone_sets or [self.zone_set]
        return set(
            FacilityIndex.objects
            .filter(build_zone_sets_covered_q(zone_sets))
            .values_list('id', flat=True)
        )

    def _partner_search_ids(self):
        """The ids the Spotlight Partners search filter returns."""
        return set(
            apply_partner_fields_or_filter(
                FacilityIndex.objects.all(),
                ['fwm_mining'],
                [self.contributor.id],
            ).values_list('id', flat=True)
        )

    def _other_zone_set(self, name='fwm_other'):
        """A second, unfiltered zone set over the west band, with its
        search membership computed (a TestCase never commits, so the
        post-commit recompute has to be run explicitly)."""
        field = PartnerField.objects.create(
            name=name, type=PartnerField.STRING, label=name,
            group=self.group, active=True,
        )
        other = ZoneSet.objects.create(
            name=name, description='Unfiltered neighbour.',
            partner_field=field, value_property='label',
        )
        with self.captureOnCommitCallbacks(execute=True):
            other.replace_zones(zone_pieces(
                feature(WEST, {'label': 'West other'}),
                value_property='label',
            ))
        return other

    # --- no filters: behaviour is unchanged -----------------------

    def test_without_filters_every_location_in_a_zone_matches(self):
        self.assertEqual(self.zone_set.filters, {})
        self.assertIsNotNone(self.provider.fetch_data(self.textile))
        self.assertEqual(
            self._search_ids(),
            {self.mine.id, self.textile.id, self.both.id},
        )

    # --- location page and v1 endpoint ---------------------------

    def test_page_applies_the_filter_rules(self):
        """Sector is an array (any shared value is enough), values in
        one key are alternatives, keys must all match, and the page
        gives the same answer for a Facility (the v1 endpoint) and a
        FacilityIndex row (the details page)."""
        with self.subTest('serves only matching locations'):
            self._set_filters({'sector': ['Mining']})
            self.assertEqual(
                self.provider.fetch_data(self.mine)['value'],
                {'raw_value': 'West report'},
            )
            self.assertIsNone(self.provider.fetch_data(self.textile))

        with self.subTest('a location in two sectors matches either'):
            self.assertEqual(
                self.provider.fetch_data(self.both)['value'],
                {'raw_value': 'East report'},
            )

        with self.subTest('values in one key are alternatives'):
            self._set_filters({'sector': ['Apparel', 'Footwear']})
            self.assertIsNone(self.provider.fetch_data(self.mine))
            self.assertIsNotNone(self.provider.fetch_data(self.textile))

        with self.subTest('keys must all match'):
            self._set_filters({'sector': ['Mining'], 'country': ['PE']})
            self.assertIsNone(self.provider.fetch_data(self.mine))
            self._set_filters({'sector': ['Mining'], 'country': ['in']})
            self.assertIsNotNone(self.provider.fetch_data(self.mine))

        with self.subTest('Facility and FacilityIndex are judged alike'):
            self._set_filters({'sector': ['Mining']})
            for facility, expected in ((self.textile, False),
                                       (self.mine, True)):
                row = FacilityIndex.objects.get(id=facility.id)
                self.assertEqual(
                    self.provider.fetch_data(row) is not None, expected
                )

    def test_product_matching_ignores_capitals_but_not_spelling(self):
        """The index holds 'sugar cane' in lower case, so a filter
        written 'Sugar Cane' must still match, on the page and in
        search. Only capitals are ignored: 'sugar' is a different
        product from 'sugarcane'."""
        with self.subTest('capitals are ignored'):
            FacilityIndex.objects.filter(id=self.textile.id).update(
                product_type=['sugar cane']
            )
            self._set_filters({'product_type': ['Sugar Cane']})
            self.assertIsNotNone(self.provider.fetch_data(self.textile))
            self.assertIsNone(self.provider.fetch_data(self.mine))
            self.assertEqual(self._search_ids(), {self.textile.id})

        with self.subTest('sugar does not match sugarcane'):
            FacilityIndex.objects.filter(id=self.textile.id).update(
                product_type=['sugarcane']
            )
            self._set_filters({'product_type': ['sugar']})
            self.assertIsNone(self.provider.fetch_data(self.textile))

    # --- sector AND product type ----------------------------------

    def _combined_set(self):
        """Filter the set to Mining AND (sugar or sugarcane), and make
        five locations that each hit a different part of that rule."""
        self._set_filters({
            'sector': ['Mining'],
            'product_type': ['sugar', 'sugarcane'],
        })
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
        least one listed product. Either alone is not enough, for a
        Facility and for a FacilityIndex row alike."""
        facilities = self._combined_set()

        shown = {
            name for name, facility in facilities.items()
            if self.provider.fetch_data(facility) is not None
        }
        self.assertEqual(shown, {'both', 'one_of_two_products'})

        for name, expected in (('both', True), ('sector_only', False),
                               ('product_only', False)):
            row = FacilityIndex.objects.get(id=facilities[name].id)
            self.assertEqual(
                self.provider.fetch_data(row) is not None, expected, name
            )

    def test_sector_and_product_agree_in_search_page_and_partner_filter(
        self,
    ):
        """Search, the Spotlight Partners filter and the location page
        all answer from one combined rule: the sector AND a listed
        product."""
        facilities = self._combined_set()
        found = self._search_ids()

        expected = {
            facilities['both'].id, facilities['one_of_two_products'].id,
        }
        for name in ('sector_only', 'product_only', 'wrong_product'):
            self.assertNotIn(facilities[name].id, found, name)
        self.assertTrue(expected <= found)

        served = {
            facility.id for facility in facilities.values()
            if self.provider.fetch_data(facility) is not None
        }
        everything = {f.id for f in facilities.values()} | {
            self.mine.id, self.textile.id, self.both.id,
        }
        self.assertEqual(served, found & everything)
        self.assertEqual(self._partner_search_ids(), expected)

    def test_adding_a_product_filter_narrows_a_sector_filter(self):
        """AND, not OR: setting the product box on top of a sector
        filter can only remove locations, never add any."""
        facilities = self._combined_set()
        self._set_filters({'sector': ['Mining']})
        sector_only = self._search_ids()

        self._set_filters({
            'sector': ['Mining'], 'product_type': ['sugar', 'sugarcane'],
        })
        combined = self._search_ids()

        self.assertTrue(combined < sector_only, (combined, sector_only))
        self.assertIn(facilities['sector_only'].id, sector_only)
        self.assertNotIn(facilities['sector_only'].id, combined)

    def test_filters_take_effect_without_a_reupload(self):
        """Filters are applied to the location when it is served, so
        changing them needs no new file."""
        self.assertIsNotNone(self.provider.fetch_data(self.textile))
        self._set_filters({'sector': ['Mining']})
        self.assertIsNone(self.provider.fetch_data(self.textile))

    def test_outside_every_zone_skips_the_filter_lookup(self):
        """A location outside every zone is the common case, so it must
        not pay for the filter query."""
        self._set_filters({'sector': ['Mining']})
        with self.assertNumQueries(1):
            self.assertIsNone(self.provider.fetch_data(self.outside))

    # --- search and spotlight -------------------------------------

    def test_search_partner_filter_and_page_apply_the_same_filters(self):
        """The shared search condition and the Spotlight Partners
        filter return the filtered locations, and the set the page
        serves is the set search returns."""
        self._set_filters({'sector': ['Mining']})
        self.assertEqual(self._search_ids(), {self.mine.id, self.both.id})
        self.assertEqual(
            self._partner_search_ids(), {self.mine.id, self.both.id}
        )

        self._set_filters({'sector': ['Apparel']})
        served = {
            facility.id
            for facility in (
                self.mine, self.textile, self.both, self.outside
            )
            if self.provider.fetch_data(facility) is not None
        }
        self.assertEqual(served, self._search_ids())

    def test_filtered_and_unfiltered_sets_combine_with_or(self):
        """A filtered set only narrows itself; an unfiltered set in the
        same search still covers everything inside its zones."""
        other = self._other_zone_set('fwm_textile')
        self._set_filters({'sector': ['Mining']})

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
        self._set_filters({'sectr': ['Mining']})

        with self.assertLogs('api.models.zone_set', level='ERROR') as logs:
            data = self.provider.fetch_data(self.mine)

        self.assertIsNone(data)
        self.assertIn('cannot be used', logs.output[0])
        self.assertIn(self.zone_set.name, logs.output[0])

    def test_unusable_stored_filters_match_nothing_in_search(self):
        """Search returns no location for the bad set instead of
        raising, and a good set searched alongside it is unaffected."""
        other = self._other_zone_set()
        self._set_filters(['not', 'a', 'dict'])

        with self.assertLogs('api.models.zone_set', level='ERROR'):
            both_sets = self._search_ids([self.zone_set, other])
            bad_alone = self._search_ids([self.zone_set])

        self.assertEqual(bad_alone, set())
        # Only the unfiltered neighbour's west band contributes.
        self.assertEqual(both_sets, {self.mine.id, self.textile.id})

    def test_only_none_and_empty_dict_are_no_filters_when_stored(self):
        """[], '' and 0 are not "no filters": they match nothing rather
        than showing the dataset on every location in its zones. {} and
        None still mean no filters."""
        for bad in ([], '', 0):
            self._set_filters(bad)
            with self.assertLogs('api.models.zone_set', level='ERROR'):
                self.assertIsNone(
                    self.provider.fetch_data(self.textile), repr(bad)
                )
                self.assertEqual(self._search_ids(), set(), repr(bad))
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
        """No boxes filled, or an empty sector choice, means no
        filters."""
        form = self._form()
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.instance.filters, {})

        form = self._form(filter_sectors=[])
        self.assertTrue(form.is_valid(), form.errors)
        self.assertNotIn('sector', form.instance.filters)

    def test_sector_picker_offers_every_os_hub_sector(self):
        """The picker is the admin's searchable multi-select and lists
        the whole sector table (OS Hub's default sectors),
        alphabetically, so any of them can be chosen."""
        Sector.objects.get_or_create(name='Mining')
        Sector.objects.get_or_create(name='Apparel')
        field = ZoneSetForm().fields['filter_sectors']

        self.assertIsInstance(field.widget, FilteredSelectMultiple)
        offered = [name for name, _ in field.choices]
        self.assertEqual(
            offered,
            sorted(Sector.objects.values_list('name', flat=True)),
        )
        self.assertIn('Mining', offered)
        self.assertIn('Apparel', offered)

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

    def test_product_box_parsing(self):
        """One product per line: blank lines and repeats are dropped,
        spaces inside a name matter, capitals do not (so two lines that
        differ only by case are one entry), and spaces, hyphens and
        plurals make different products."""
        cases = (
            ('sugar\n\n  sugarcane \nsugar\n', ['sugar', 'sugarcane']),
            ('Sugar Cane\nsugar cane', ['sugar cane']),
            ('sugarcane\nsugar cane\nsugar-cane',
             ['sugarcane', 'sugar cane', 'sugar-cane']),
        )
        for text, expected in cases:
            with self.subTest(text=text):
                form = self._form(filter_product_types=text)
                self.assertTrue(form.is_valid(), form.errors)
                self.assertEqual(
                    form.instance.filters, {'product_type': expected}
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

    def test_boxes_combine_into_one_and_setting(self):
        """All the boxes feed one filters setting, which the rule treats
        as AND across keys: a location needs a chosen sector and a
        listed product (and the advanced keys when set)."""
        Sector.objects.get_or_create(name='Mining')
        Sector.objects.get_or_create(name='Agriculture')

        form = self._form(
            filter_sectors=['Mining'],
            filter_product_types='sugar\nsugarcane',
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(
            form.instance.filters,
            {'sector': ['Mining'], 'product_type': ['sugar', 'sugarcane']},
        )
        self.assertEqual(
            build_filters_q(form.instance.filters).connector, Q.AND
        )

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

    def test_help_text_states_the_rules_to_staff(self):
        """The format and the AND rule have to be stated on the form
        itself."""
        fields = ZoneSetForm().fields
        sector_help = fields['filter_sectors'].help_text
        product = fields['filter_product_types']

        self.assertIn('ALL of the filled boxes', sector_help)
        self.assertIn('AND', sector_help)
        self.assertIn('must match both', product.help_text)
        self.assertIn('ONE product type per line', product.help_text)
        self.assertIn('Do not use commas', product.help_text)
        self.assertIn('Capital letters do not matter', product.help_text)
        self.assertIn('placeholder', product.widget.attrs)

    def test_product_box_limit(self):
        """One mistaken paste must not become an enormous filter:
        exactly the limit is accepted, one more is refused."""
        at_limit = '\n'.join(
            f'product {i}' for i in range(MAX_VALUES_PER_FILTER)
        )
        form = self._form(filter_product_types=at_limit)
        self.assertTrue(form.is_valid(), form.errors)

        form = self._form(filter_product_types=at_limit + '\none more')
        self.assertFalse(form.is_valid())
        self.assertIn('the limit is', str(form.non_field_errors()))

    def test_filter_boxes_have_a_length_limit(self):
        form = self._form(filter_product_types='a' * 10001)
        self.assertFalse(form.is_valid())
        self.assertIn('filter_product_types', form.errors)
        form = self._form(filter_other='x' * 5001)
        self.assertFalse(form.is_valid())
        self.assertIn('filter_other', form.errors)

    def test_other_box_refuses_bad_input(self):
        """Invalid JSON, keys that have their own box, unknown keys and
        empty lists are all refused (an empty list would match no
        location, so the field would silently never show)."""
        cases = (
            ('{country: KH', 'filter_other', 'Not valid JSON'),
            ('{"sector": ["Mining"]}', 'filter_other', 'cannot be set here'),
            ('{"countri": ["KH"]}', 'filter_other', None),
            ('{"country": []}', None, 'at least one value'),
        )
        for text, field, message in cases:
            with self.subTest(text=text):
                form = self._form(filter_other=text)
                self.assertFalse(form.is_valid())
                if field:
                    self.assertIn(field, form.errors)
                if message and field:
                    self.assertIn(message, str(form.errors[field]))
                elif message:
                    self.assertIn(message, str(form.non_field_errors()))

    def test_edit_form_shows_the_saved_filters_and_keeps_retired_sectors(
        self,
    ):
        """Opening a saved set shows its filters, and a sector the
        taxonomy no longer lists stays a choice, so opening and saving
        the set does not silently drop it."""
        Sector.objects.get_or_create(name='Mining')
        self._set_filters({
            'sector': ['Mining', 'Retired sector'],
            'product_type': ['sugar', 'sugarcane'],
            'country': ['PE'],
        })

        form = ZoneSetForm(instance=ZoneSet.objects.get(pk=self.zone_set.pk))

        self.assertEqual(
            form.initial['filter_sectors'], ['Mining', 'Retired sector']
        )
        self.assertEqual(
            form.initial['filter_product_types'], 'sugar\nsugarcane'
        )
        self.assertEqual(form.initial['filter_other'], '{"country": ["PE"]}')
        offered = [name for name, _ in form.fields['filter_sectors'].choices]
        self.assertIn('Retired sector', offered)

    def test_editing_filters_later_keeps_the_zones(self):
        """Filters are applied to locations at serve time, so adding,
        changing or clearing them on a set that already has zones needs
        no new file."""
        Sector.objects.get_or_create(name='Mining')
        self._set_filters({'sector': ['Mining']})

        add = self._edit_form(
            filter_sectors=['Mining'],
            filter_product_types='sugar\nsugarcane',
        )
        self.assertTrue(add.is_valid(), add.errors)
        self.assertIsNone(add.parsed_zones)
        self.assertEqual(
            add.instance.filters,
            {'sector': ['Mining'], 'product_type': ['sugar', 'sugarcane']},
        )

        clear = self._edit_form()
        self.assertTrue(clear.is_valid(), clear.errors)
        self.assertIsNone(clear.parsed_zones)
        self.assertEqual(clear.instance.filters, {})

    def test_editing_other_things_does_not_disturb_the_filters(self):
        """Saving the saved values back leaves the filters as they were
        and still allows the rest of the set to be edited."""
        Sector.objects.get_or_create(name='Mining')
        self._set_filters({
            'sector': ['Mining'], 'product_type': ['sugar'],
        })
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

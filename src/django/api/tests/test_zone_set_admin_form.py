from unittest.mock import Mock, patch

from django.conf import settings
from django.contrib.admin.sites import AdminSite
from django.contrib.gis.geos import Point
from django.test import TestCase, override_settings
from django.urls import reverse
from waffle.testutils import override_switch

from api.helpers.geojson_polygon import InvalidPolygonGeoJSON
from api.helpers.zone_subdivision import subdivide_zone_records
from api.models import PartnerField, User, Zone, ZoneSet
from api.models.zone_set_admin import ZoneSetAdmin, ZoneSetForm
from api.partner_fields.registry import ZONE_SETS_SWITCH
from api.tests.zone_fixtures import DISC, feature, records, upload

LEFT = [[[0, 0], [0, 10], [5, 10], [5, 0], [0, 0]]]
RIGHT = [[[5, 0], [5, 10], [10, 10], [10, 0], [5, 0]]]
FAR = [[[20, 20], [20, 30], [30, 30], [30, 20], [20, 20]]]


BASE_DATA = {
    'name': 'water_stress',
    'description': 'Baseline water stress bands for tests.',
    'value_property': 'bws_label',
    'active': True,
}

# Data for a set feeding an object field: no value property, the
# feature properties are read by the schema's keys instead.
OBJECT_DATA = {
    'name': 'water_risk',
    'description': 'Aqueduct water risk, several values per basin.',
    'active': True,
}

SCHEMA = {
    'type': 'object',
    'properties': {
        'bws_label': {'type': 'string', 'title': 'Water stress, today'},
        'bwd_label': {'type': 'string', 'title': 'Drought risk'},
        'atlas_url': {
            'type': 'string', 'format': 'uri',
            'title': 'Aqueduct Water Risk Atlas',
        },
    },
    'required': ['bws_label', 'bwd_label'],
}


def object_field(schema=SCHEMA, name='aqueduct_water_risk'):
    """An object-type partner field with the given JSON schema."""
    return PartnerField.objects.create(
        name=name, type=PartnerField.OBJECT, label='Water risk',
        json_schema=schema,
    )


class ZoneSetFormTest(TestCase):
    """Tests for validating a zone set upload in the admin form."""

    def test_requires_a_file_on_create(self):
        form = ZoneSetForm(data=BASE_DATA)
        self.assertFalse(form.is_valid())
        self.assertIn('Upload a GeoJSON', str(form.errors))

    def test_valid_upload_parses_one_zone_per_feature(self):
        form = ZoneSetForm(
            data=BASE_DATA,
            files={'geojson_file': upload(
                feature(LEFT, {'bws_label': 'High'}),
                feature(RIGHT, {'bws_label': 'Low'}),
            )},
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(
            [zone['label'] for zone in form.parsed_zones], ['High', 'Low']
        )

    def test_large_feature_is_parsed_into_pieces(self):
        """The form hands save_model storage pieces, not features: a
        feature over the vertex budget arrives as several pieces that
        all carry its label and position."""
        form = ZoneSetForm(
            data=BASE_DATA,
            files={'geojson_file': upload(
                feature(DISC, {'bws_label': 'High'}),
                feature(LEFT, {'bws_label': 'Low'}),
            )},
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertGreater(len(form.parsed_zones), 2)
        self.assertEqual(
            {(p['feature_index'], p['label']) for p in form.parsed_zones},
            {(0, 'High'), (1, 'Low')},
        )

    def test_subdivision_refusal_is_a_form_error(self):
        """A feature PostGIS returns no piece for is reported on the
        form like any other bad file, not raised at save time."""
        with patch(
            'api.models.zone_set_admin.subdivide_zone_records',
            side_effect=InvalidPolygonGeoJSON(
                'ST_Subdivide returned no pieces for feature(s) at '
                'position(s) [1]; the upload was refused rather than '
                'saved without them.'
            ),
        ):
            form = ZoneSetForm(
                data=BASE_DATA,
                files={'geojson_file': upload(
                    feature(LEFT, {'bws_label': 'High'}),
                    feature(RIGHT, {'bws_label': 'Low'}),
                )},
            )
            self.assertFalse(form.is_valid())
        self.assertIn('no pieces for feature(s) at position(s) [1]',
                      str(form.errors))
        self.assertIsNone(form.parsed_zones)

    def test_missing_value_property_is_a_form_error_with_a_count(self):
        form = ZoneSetForm(
            data=BASE_DATA,
            files={'geojson_file': upload(
                feature(LEFT, {'bws_label': 'High'}),
                feature(RIGHT, {'nope': 1}),
            )},
        )
        self.assertFalse(form.is_valid())
        self.assertIn('1 of 2 feature(s) are missing', str(form.errors))
        self.assertIsNone(form.parsed_zones)

    def test_projected_coordinates_are_a_form_error(self):
        metres = [[[233000, 1500000], [233000, 1600000],
                   [333000, 1600000], [333000, 1500000],
                   [233000, 1500000]]]
        form = ZoneSetForm(
            data=BASE_DATA,
            files={'geojson_file': upload(
                feature(metres, {'bws_label': 'High'}),
            )},
        )
        self.assertFalse(form.is_valid())
        self.assertIn('projected coordinate system', str(form.errors))

    def test_invalid_geometry_is_a_form_error(self):
        bowtie = [[[0, 0], [10, 10], [10, 0], [0, 10], [0, 0]]]
        form = ZoneSetForm(
            data=BASE_DATA,
            files={'geojson_file': upload(
                feature(bowtie, {'bws_label': 'High'}),
            )},
        )
        self.assertFalse(form.is_valid())
        self.assertIn('not valid', str(form.errors))

    def test_oversized_file_is_rejected(self):
        big = upload(feature(LEFT, {'bws_label': 'High'}))
        big.size = ZoneSetForm.GEOJSON_FILE_MAX_BYTES + 1
        form = ZoneSetForm(data=BASE_DATA, files={'geojson_file': big})
        self.assertFalse(form.is_valid())
        self.assertIn('too large', str(form.errors))

    def test_name_must_be_identifier_style(self):
        form = ZoneSetForm(
            data={**BASE_DATA, 'name': 'water stress!'},
            files={'geojson_file': upload(
                feature(LEFT, {'bws_label': 'High'}),
            )},
        )
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

    def _form_with_field(self, partner_field, instance=None):
        return ZoneSetForm(
            data={**BASE_DATA, 'partner_field': partner_field.pk},
            files={'geojson_file': upload(
                feature(LEFT, {'bws_label': 'High'}),
            )},
            instance=instance,
        )

    def test_inactive_partner_field_can_be_linked(self):
        """The default manager hides inactive fields; the form must
        not, or a set whose field was deactivated could never be
        edited or retired, and a dataset could not be staged against
        a field that is not switched on yet."""
        inactive = PartnerField.objects.create(
            name='staged_dataset', type=PartnerField.STRING,
            label='Staged', active=False,
        )

        form = self._form_with_field(inactive)

        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['partner_field'], inactive)

    def test_set_linked_to_deactivated_field_can_still_be_edited(self):
        field = PartnerField.objects.create(
            name='water_stress_field', type=PartnerField.STRING,
            label='Water stress',
        )
        zone_set = ZoneSet.objects.create(
            name='water_stress', description='x',
            partner_field=field, value_property='bws_label',
        )
        field.active = False
        field.save()

        form = ZoneSetForm(
            data={**BASE_DATA, 'partner_field': field.pk, 'active': False},
            instance=zone_set,
        )

        self.assertTrue(form.is_valid(), form.errors)

    def test_int_and_float_partner_fields_are_rejected(self):
        """The provider emits a string or a keyed object, so an
        int/float field would serve a mis-shaped value."""
        for field_type in (PartnerField.INT, PartnerField.FLOAT):
            with self.subTest(field_type=field_type):
                field = PartnerField.objects.create(
                    name=f'{field_type}_field', type=field_type,
                    label='Typed',
                )
                form = self._form_with_field(field)
                self.assertFalse(form.is_valid())
                self.assertIn('partner_field', form.errors)
                self.assertIn(field_type, str(form.errors['partner_field']))

    # --- object fields (OSDEV-3659) --------------------------------

    def _object_form(self, partner_field, *features, data=None,
                     instance=None):
        return ZoneSetForm(
            data={**OBJECT_DATA, 'partner_field': partner_field.pk,
                  **(data or {})},
            files={'geojson_file': upload(*features)} if features else None,
            instance=instance,
        )

    def test_object_field_with_schema_is_accepted(self):
        """No value property is needed: each zone is read one feature
        property per schema key, labelled by the first required one."""
        form = self._object_form(
            object_field(),
            feature(LEFT, {'bws_label': 'High', 'bwd_label': 'Low'}),
            feature(RIGHT, {'bws_label': 'Low', 'bwd_label': 'Medium',
                            'atlas_url': 'https://example.org/r'}),
        )

        self.assertTrue(form.is_valid(), form.errors)
        self.assertIsNone(form.cleaned_data['value_property'])
        self.assertEqual(
            [zone['label'] for zone in form.parsed_zones], ['High', 'Low']
        )

    def test_object_field_without_schema_is_rejected(self):
        """AC #4: an object field gives the page nothing to render by
        and the upload nothing to validate against until it has a
        schema with a properties map."""
        for index, schema in enumerate(
            (None, {}, {'type': 'object'}, {'properties': {}},
             {'properties': 'bws_label'})
        ):
            with self.subTest(schema=schema):
                field = object_field(schema=schema, name=f'no_schema_{index}')
                form = self._object_form(
                    field, feature(LEFT, {'bws_label': 'High'})
                )
                self.assertFalse(form.is_valid())
                self.assertIn('schema is required',
                              str(form.errors['partner_field']))

    def test_value_property_is_required_for_a_string_field(self):
        """The column is optional for object sets only; a string set,
        linked or not, still needs the key to read labels by."""
        string_field = PartnerField.objects.create(
            name='bands', type=PartnerField.STRING, label='Bands',
        )
        for partner_field in (None, string_field.pk):
            with self.subTest(partner_field=partner_field):
                form = ZoneSetForm(
                    data={**OBJECT_DATA, 'partner_field': partner_field},
                    files={'geojson_file': upload(
                        feature(LEFT, {'bws_label': 'High'}),
                    )},
                )
                self.assertFalse(form.is_valid())
                self.assertIn('value_property', form.errors)
                self.assertIsNone(form.parsed_zones)

    def test_value_property_is_cleared_for_an_object_field(self):
        """Whatever was typed is ignored for an object field, and
        cleared rather than saved as a stale setting."""
        form = self._object_form(
            object_field(),
            feature(LEFT, {'bws_label': 'High', 'bwd_label': 'Low'}),
            data={'value_property': 'bws_label'},
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertIsNone(form.cleaned_data['value_property'])

    def test_upload_missing_a_required_key_is_rejected(self):
        """AC #3: the error names the key and the number of features
        lacking it; keys outside `required` may be absent."""
        form = self._object_form(
            object_field(),
            feature(LEFT, {'bws_label': 'High', 'bwd_label': 'Low'}),
            feature(RIGHT, {'bws_label': 'Low'}),
            feature(FAR, {'bws_label': 'Low', 'bwd_label': ''}),
        )

        self.assertFalse(form.is_valid())
        message = str(form.errors)
        self.assertIn('2 of 3 feature(s) are missing the', message)
        self.assertIn('bwd_label', message)
        self.assertNotIn('atlas_url', message)
        self.assertIsNone(form.parsed_zones)

    def test_switching_to_an_object_field_without_a_file_is_refused(self):
        """A set with zones that moves to, from or between object
        fields must be re-read from the file: the stored zones were
        validated against (and are served by) the old field's schema.
        Moving between string fields keeps the same shape."""
        string_a = PartnerField.objects.create(
            name='string_a', type=PartnerField.STRING, label='A',
        )
        string_b = PartnerField.objects.create(
            name='string_b', type=PartnerField.STRING, label='B',
        )
        object_a = object_field(name='object_a')
        object_b = object_field(name='object_b')
        zone_set = ZoneSet.objects.create(
            name='water_stress', description='x',
            partner_field=string_a, value_property='bws_label',
        )
        zone_set.replace_zones(subdivide_zone_records(records(
            feature(LEFT, {'bws_label': 'High', 'bwd_label': 'Low'}),
        )))

        form = ZoneSetForm(
            data={**BASE_DATA, 'partner_field': string_b.pk},
            instance=zone_set,
        )
        self.assertTrue(form.is_valid(), form.errors)

        form = ZoneSetForm(
            data={**BASE_DATA, 'partner_field': object_a.pk},
            instance=zone_set,
        )
        self.assertFalse(form.is_valid())
        self.assertIn('Upload the file again',
                      str(form.errors['partner_field']))

        zone_set.partner_field = object_a
        zone_set.value_property = None
        zone_set.save()
        for target in (object_b, string_a, None):
            with self.subTest(target=target):
                form = ZoneSetForm(
                    data={**OBJECT_DATA,
                          'partner_field': target.pk if target else None,
                          'value_property': 'bws_label'},
                    instance=zone_set,
                )
                self.assertFalse(form.is_valid())
                self.assertIn('partner_field', form.errors)

        # Leaving the object field as it is needs nothing.
        form = ZoneSetForm(
            data={**OBJECT_DATA, 'partner_field': object_a.pk,
                  'description': 'Edited.'},
            instance=zone_set,
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_partner_field_of_a_hard_wired_provider_is_rejected(self):
        """Linking e.g. `mit_living_wage` would give the registry two
        providers for one field name."""
        for name in ('mit_living_wage', 'wage_indicator',
                     'india_labour_line_helpline'):
            with self.subTest(name=name):
                # These fields are seeded by migrations, active or not.
                field, _ = (
                    PartnerField.objects.get_all_including_inactive()
                    .get_or_create(
                        name=name,
                        defaults={'type': PartnerField.STRING,
                                  'label': name},
                    )
                )
                field.type = PartnerField.STRING
                field.save()
                form = self._form_with_field(field)
                self.assertFalse(form.is_valid())
                self.assertIn('built-in provider',
                              str(form.errors['partner_field']))


class ZoneSetAdminSaveTest(TestCase):
    """Tests for how the admin saves and replaces a set's zones."""

    def setUp(self):
        self.model_admin = ZoneSetAdmin(ZoneSet, AdminSite())
        self.request = Mock()

    def _save(self, data, files=None, instance=None):
        """Run the form and admin save the way the change view does."""
        form = ZoneSetForm(data=data, files=files, instance=instance)
        self.assertTrue(form.is_valid(), form.errors)
        obj = form.save(commit=False)
        self.model_admin.save_model(
            self.request, obj, form, change=instance is not None
        )
        return obj

    def test_create_saves_zones_with_geometry_and_properties(self):
        zone_set = self._save(
            BASE_DATA,
            files={'geojson_file': upload(
                feature(LEFT, {'bws_label': 'High', 'bws_score': 3.2}),
                feature(RIGHT, {'bws_label': 'Low', 'bws_score': 0.4}),
            )},
        )

        zones = list(zone_set.zones.order_by('feature_index'))
        self.assertEqual(len(zones), 2)
        self.assertEqual(zones[0].feature_index, 0)
        self.assertEqual(zones[0].label, 'High')
        self.assertEqual(
            zones[0].value['properties'],
            {'bws_label': 'High', 'bws_score': 3.2},
        )
        self.assertTrue(zones[0].geom.contains(Point(2, 5, srid=4326)))
        self.assertTrue(zones[1].geom.contains(Point(8, 5, srid=4326)))
        self.assertEqual(zone_set.resolve_zone(Point(8, 5, srid=4326)).label,
                         'Low')

    def test_edit_without_file_keeps_zones(self):
        zone_set = self._save(
            BASE_DATA,
            files={'geojson_file': upload(
                feature(LEFT, {'bws_label': 'High'}),
            )},
        )
        before = list(zone_set.zones.values_list('id', flat=True))

        self._save(
            {**BASE_DATA, 'description': 'Edited description.'},
            instance=zone_set,
        )

        zone_set.refresh_from_db()
        self.assertEqual(zone_set.description, 'Edited description.')
        self.assertEqual(
            list(zone_set.zones.values_list('id', flat=True)), before
        )

    def test_changing_value_property_without_file_is_refused(self):
        """Stored labels were read with the old key, so the change
        must come with a re-upload."""
        zone_set = self._save(
            BASE_DATA,
            files={'geojson_file': upload(
                feature(LEFT, {'bws_label': 'High', 'bws_cat': 4}),
            )},
        )

        form = ZoneSetForm(
            data={**BASE_DATA, 'value_property': 'bws_cat'},
            instance=zone_set,
        )

        self.assertFalse(form.is_valid())
        self.assertIn('value_property', form.errors)

    def test_reupload_replaces_zones(self):
        zone_set = self._save(
            BASE_DATA,
            files={'geojson_file': upload(
                feature(LEFT, {'bws_label': 'High'}),
                feature(RIGHT, {'bws_label': 'Low'}),
            )},
        )
        old_ids = set(zone_set.zones.values_list('id', flat=True))

        self._save(
            {**BASE_DATA, 'value_property': 'bws_cat'},
            files={'geojson_file': upload(
                feature(FAR, {'bws_cat': 'Extremely high'}),
            )},
            instance=zone_set,
        )

        zones = list(zone_set.zones.all())
        self.assertEqual([zone.label for zone in zones], ['Extremely high'])
        self.assertFalse(old_ids & {zone.id for zone in zones})
        self.assertFalse(Zone.objects.filter(id__in=old_ids).exists())

    def test_reupload_queues_the_search_recompute_and_tells_staff(self):
        """Saving a file replaces the zones, queues the recompute of
        `FacilityIndex.zone_set_ids` for commit, and tells staff that
        search results lag until it finishes. Editing without a file
        does neither."""
        recompute_path = (
            'api.facility_index_backfill.zone_set_ids_recompute.'
            'recompute_zone_set_ids'
        )
        with patch(recompute_path) as recompute:
            with self.captureOnCommitCallbacks(execute=True):
                zone_set = self._save(
                    BASE_DATA,
                    files={'geojson_file': upload(
                        feature(LEFT, {'bws_label': 'High'}),
                    )},
                )
            recompute.assert_called_once_with()
            self.request._messages.add.assert_called_once()
            message = self.request._messages.add.call_args.args[1]
            self.assertIn('recomputed in the background', message)

            recompute.reset_mock()
            self.request._messages.add.reset_mock()
            with self.captureOnCommitCallbacks(execute=True):
                self._save(
                    {**BASE_DATA, 'description': 'Edited.'},
                    instance=zone_set,
                )
            recompute.assert_not_called()
            self.request._messages.add.assert_not_called()

    def test_failed_reupload_leaves_old_zones_serving(self):
        """A bad replacement file is refused before any row changes,
        so the previous zones stay exactly as they were (AC #5)."""
        zone_set = self._save(
            BASE_DATA,
            files={'geojson_file': upload(
                feature(LEFT, {'bws_label': 'High'}),
            )},
        )
        before = list(zone_set.zones.values_list('id', 'value'))

        form = ZoneSetForm(
            data=BASE_DATA,
            files={'geojson_file': upload(
                feature(LEFT, {'bws_label': 'High'}),
                feature(RIGHT, {'missing': True}),
            )},
            instance=zone_set,
        )

        self.assertFalse(form.is_valid())
        self.assertEqual(
            list(zone_set.zones.values_list('id', 'value')), before
        )
        self.assertEqual(
            zone_set.resolve_zone(Point(2, 5, srid=4326)).label, 'High'
        )

    def test_replace_zones_is_all_or_nothing(self):
        """If inserting the new zones fails mid-way, the delete rolls
        back too and the old zones remain."""
        zone_set = self._save(
            BASE_DATA,
            files={'geojson_file': upload(
                feature(LEFT, {'bws_label': 'High'}),
            )},
        )
        before = list(zone_set.zones.values_list('id', flat=True))
        broken = [
            {'geom': None, 'label': 'x', 'properties': {}},
        ]

        with self.assertRaises(Exception):
            zone_set.replace_zones(broken)

        self.assertEqual(
            list(zone_set.zones.values_list('id', flat=True)), before
        )

    def test_zone_count_uses_the_list_annotation(self):
        """The list column reads the annotated count, including zero,
        and only falls back to a query when no annotation is present."""
        zone_set = self._save(
            BASE_DATA,
            files={'geojson_file': upload(
                feature(LEFT, {'bws_label': 'High'}),
            )},
        )
        annotated = self.model_admin.get_queryset(self.request).get(
            pk=zone_set.pk
        )
        self.assertEqual(self.model_admin.zone_count(annotated), 1)

        zone_set.zones.all().delete()
        annotated_empty = self.model_admin.get_queryset(self.request).get(
            pk=zone_set.pk
        )
        with self.assertNumQueries(0):
            self.assertEqual(self.model_admin.zone_count(annotated_empty), 0)
        self.assertEqual(self.model_admin.zone_count(zone_set), 0)

    def test_zone_summary_describes_saved_zones(self):
        zone_set = self._save(
            BASE_DATA,
            files={'geojson_file': upload(
                feature(LEFT, {'bws_label': 'High'}),
                feature(RIGHT, {'bws_label': 'Low'}),
                feature(FAR, {'bws_label': 'High'}),
            )},
        )

        # One count plus one distinct-labels query; the zones' full
        # JSON is never loaded.
        with self.assertNumQueries(2):
            summary = self.model_admin.zone_summary(zone_set)

        self.assertIn('3 zone(s) stored as 3 piece(s)', summary)
        self.assertIn('High, Low', summary)
        self.assertEqual(
            self.model_admin.zone_summary(ZoneSet()), '(no zones saved yet)'
        )

    def test_counts_are_of_features_not_pieces(self):
        """A feature stored as several pieces is one zone in the list
        column and the summary; the summary also says how many pieces
        the set is stored as."""
        zone_set = self._save(
            BASE_DATA,
            files={'geojson_file': upload(
                feature(DISC, {'bws_label': 'High'}),
                feature(LEFT, {'bws_label': 'Low'}),
            )},
        )
        pieces = zone_set.zones.count()
        self.assertGreater(pieces, 2)

        annotated = self.model_admin.get_queryset(self.request).get(
            pk=zone_set.pk
        )
        self.assertEqual(self.model_admin.zone_count(annotated), 2)
        self.assertEqual(self.model_admin.zone_count(zone_set), 2)
        self.assertIn(
            f'2 zone(s) stored as {pieces} piece(s)',
            self.model_admin.zone_summary(zone_set),
        )

    def test_object_upload_stores_label_and_properties(self):
        """A set feeding an object field stores the first required
        property as the label and the whole feature as properties, in
        the same `Zone.value` shape as a string set (no new column)."""
        zone_set = self._save(
            {**OBJECT_DATA, 'partner_field': object_field().pk},
            files={'geojson_file': upload(
                feature(LEFT, {'bws_label': 'High', 'bwd_label': 'Low',
                               'atlas_url': 'https://example.org/l',
                               'pfaf_id': 1}),
            )},
        )

        zone_set.refresh_from_db()
        self.assertIsNone(zone_set.value_property)
        [zone] = zone_set.zones.all()
        self.assertEqual(zone.value, {
            'label': 'High',
            'properties': {'bws_label': 'High', 'bwd_label': 'Low',
                           'atlas_url': 'https://example.org/l',
                           'pfaf_id': 1},
        })
        self.assertEqual(
            zone_set.resolve_zone(Point(2, 5, srid=4326)).label, 'High'
        )

    def test_failed_object_reupload_leaves_old_zones_serving(self):
        """AC #3: a replacement file lacking a required key is refused
        before any row changes."""
        zone_set = self._save(
            {**OBJECT_DATA, 'partner_field': object_field().pk},
            files={'geojson_file': upload(
                feature(LEFT, {'bws_label': 'High', 'bwd_label': 'Low'}),
            )},
        )
        before = list(zone_set.zones.values_list('id', 'value'))

        form = ZoneSetForm(
            data={**OBJECT_DATA, 'partner_field': zone_set.partner_field.pk},
            files={'geojson_file': upload(
                feature(LEFT, {'bws_label': 'High', 'bwd_label': 'Low'}),
                feature(RIGHT, {'bws_label': 'Low'}),
            )},
            instance=zone_set,
        )

        self.assertFalse(form.is_valid())
        self.assertIn('1 of 2 feature(s)', str(form.errors))
        self.assertEqual(
            list(zone_set.zones.values_list('id', 'value')), before
        )

    def test_zone_summary_lists_schema_keys_for_an_object_field(self):
        """Staff check an object set against the keys it serves, not
        a label that is only the first required property."""
        zone_set = self._save(
            {**OBJECT_DATA, 'partner_field': object_field().pk},
            files={'geojson_file': upload(
                feature(LEFT, {'bws_label': 'High', 'bwd_label': 'Low'}),
                feature(RIGHT, {'bws_label': 'Low', 'bwd_label': 'Low'}),
            )},
        )

        summary = self.model_admin.zone_summary(zone_set)

        self.assertIn('2 zone(s) stored as 2 piece(s)', summary)
        self.assertIn(
            'serving schema keys: bws_label, bwd_label, atlas_url', summary
        )
        self.assertNotIn('labels:', summary)


# The admin templates call `{% static %}`, and the project's manifest
# storage then wants a `staticfiles.json` that only `collectstatic`
# writes. CI never runs it, so render against the plain storage.
@override_settings(STORAGES={
    **settings.STORAGES,
    'staticfiles': {
        'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
    },
})
class ZoneSetAdminSwitchNoticeTest(TestCase):
    """
    The zone set screens say when `enable_zone_sets` is off, because
    an uploaded, linked, active set then serves nothing on any
    location page and the switch is on a different admin screen.
    """

    NOTICE = 'switch is off, so no zone set serves values'

    def setUp(self):
        superuser = User.objects.create_superuser(
            email='super@example.com', password='example123'
        )
        self.client.force_login(superuser)
        self.zone_set = ZoneSet.objects.create(
            name='water_stress', description='d', value_property='v'
        )

    def test_list_and_change_pages_warn_while_switch_is_off(self):
        with override_switch(ZONE_SETS_SWITCH, active=False):
            for url in (
                reverse('admin:api_zoneset_changelist'),
                reverse('admin:api_zoneset_add'),
                reverse(
                    'admin:api_zoneset_change', args=[self.zone_set.pk]
                ),
            ):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200, url)
                self.assertContains(response, self.NOTICE, msg_prefix=url)
                self.assertContains(
                    response, reverse('admin:waffle_switch_changelist'),
                    msg_prefix=url,
                )

    def test_no_warning_while_switch_is_on(self):
        with override_switch(ZONE_SETS_SWITCH, active=True):
            response = self.client.get(
                reverse('admin:api_zoneset_changelist')
            )
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.NOTICE)

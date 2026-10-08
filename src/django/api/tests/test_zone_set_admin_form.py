import json
from unittest.mock import Mock

from django.contrib.admin.sites import AdminSite
from django.contrib.gis.geos import Point
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from api.models import PartnerField, Zone, ZoneSet
from api.models.zone_set_admin import ZoneSetAdmin, ZoneSetForm

LEFT = [[[0, 0], [0, 10], [5, 10], [5, 0], [0, 0]]]
RIGHT = [[[5, 0], [5, 10], [10, 10], [10, 0], [5, 0]]]
FAR = [[[20, 20], [20, 30], [30, 30], [30, 20], [20, 20]]]


def feature(coordinates, properties):
    return {
        'type': 'Feature',
        'properties': properties,
        'geometry': {'type': 'Polygon', 'coordinates': coordinates},
    }


def upload(*features, name='zones.geojson'):
    """Build an uploaded FeatureCollection file."""
    raw = json.dumps({'type': 'FeatureCollection', 'features': features})
    return SimpleUploadedFile(
        name, raw.encode('utf-8'), content_type='application/geo+json'
    )


BASE_DATA = {
    'name': 'water_stress',
    'description': 'Baseline water stress bands for tests.',
    'value_property': 'bws_label',
    'active': True,
}


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

    def test_non_string_partner_field_is_rejected(self):
        """The provider emits a plain string, so an object/int/float
        field would serve a mis-shaped value."""
        for field_type in (PartnerField.OBJECT, PartnerField.INT,
                           PartnerField.FLOAT):
            with self.subTest(field_type=field_type):
                field = PartnerField.objects.create(
                    name=f'{field_type}_field', type=field_type,
                    label='Typed',
                )
                form = self._form_with_field(field)
                self.assertFalse(form.is_valid())
                self.assertIn('partner_field', form.errors)
                self.assertIn(field_type, str(form.errors['partner_field']))

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

        self.assertIn('3 zone(s)', summary)
        self.assertIn('High, Low', summary)
        self.assertEqual(
            self.model_admin.zone_summary(ZoneSet()), '(no zones saved yet)'
        )

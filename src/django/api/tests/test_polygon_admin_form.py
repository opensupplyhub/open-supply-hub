import json

from django.contrib.admin.sites import AdminSite
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory, TestCase
from waffle.testutils import override_switch

from api.admin import (
    POLYGONS_SWITCH,
    PolygonAdmin,
    PolygonForm,
)
from api.models import Polygon, User

SQUARE_GEOJSON = json.dumps({
    'type': 'Polygon',
    'coordinates': [[[0, 0], [0, 10], [10, 10], [10, 0], [0, 0]]],
})


class PolygonFormTest(TestCase):
    def test_requires_a_geometry_on_create(self):
        form = PolygonForm(data={
            'name': 'no_shape',
            'description': 'Missing a boundary.',
        })
        self.assertFalse(form.is_valid())

    def test_rejects_invalid_geojson(self):
        form = PolygonForm(data={
            'name': 'bad_shape',
            'description': 'Has malformed GeoJSON.',
            'geojson_text': 'not json',
        })
        self.assertFalse(form.is_valid())

    def test_accepts_pasted_geojson_text(self):
        form = PolygonForm(data={
            'name': 'pasted_square',
            'description': 'A square pasted as text.',
            'geojson_text': SQUARE_GEOJSON,
        })
        self.assertTrue(form.is_valid(), form.errors)
        instance = form.save()
        self.assertEqual(instance.geom.geom_type, 'MultiPolygon')

    def test_accepts_uploaded_geojson_file(self):
        upload = SimpleUploadedFile(
            'boundary.geojson',
            SQUARE_GEOJSON.encode('utf-8'),
            content_type='application/geo+json',
        )
        form = PolygonForm(
            data={
                'name': 'uploaded_square',
                'description': 'A square uploaded as a file.',
            },
            files={'geojson_file': upload},
        )
        self.assertTrue(form.is_valid(), form.errors)
        instance = form.save()
        self.assertEqual(instance.geom.geom_type, 'MultiPolygon')


class PolygonAdminSwitchTest(TestCase):
    def setUp(self):
        self.model_admin = PolygonAdmin(Polygon, AdminSite())
        self.request = RequestFactory().get('/')
        self.request.user = User.objects.create_superuser(
            'admin@example.com', 'example123'
        )

    def _permissions(self):
        return (
            self.model_admin.has_module_permission(self.request),
            self.model_admin.has_view_permission(self.request),
            self.model_admin.has_add_permission(self.request),
            self.model_admin.has_change_permission(self.request),
            self.model_admin.has_delete_permission(self.request),
        )

    @override_switch(POLYGONS_SWITCH, active=False)
    def test_admin_is_hidden_when_switch_is_off(self):
        self.assertEqual(self._permissions(), (False,) * 5)

    @override_switch(POLYGONS_SWITCH, active=True)
    def test_admin_is_available_when_switch_is_on(self):
        self.assertEqual(self._permissions(), (True,) * 5)


class PolygonAdminDisplayTest(TestCase):
    def _make_polygon(self):
        form = PolygonForm(data={
            'name': 'display_square',
            'description': 'A square for display tests.',
            'geojson_text': SQUARE_GEOJSON,
        })
        self.assertTrue(form.is_valid(), form.errors)
        return form.save()

    def test_edit_form_prefills_saved_geojson(self):
        polygon = self._make_polygon()

        form = PolygonForm(instance=polygon)

        initial = form.fields['geojson_text'].initial
        self.assertIsNotNone(initial)
        self.assertIn('MultiPolygon', initial)
        # Round-trip: the prefilled text re-parses to the same shape.
        resubmitted = PolygonForm(
            data={
                'name': polygon.name,
                'description': polygon.description,
                'geojson_text': initial,
            },
            instance=polygon,
        )
        self.assertTrue(resubmitted.is_valid(), resubmitted.errors)
        self.assertTrue(
            resubmitted.save().geom.equals(polygon.geom)
        )

    def test_boundary_summary_describes_geometry(self):
        polygon = self._make_polygon()
        model_admin = PolygonAdmin(Polygon, AdminSite())

        summary = model_admin.boundary_summary(polygon)

        self.assertIn('1 part(s)', summary)
        self.assertIn('5 vertices', summary)
        self.assertIn('0.000, 0.000, 10.000, 10.000', summary)

    def test_boundary_summary_handles_unsaved_polygon(self):
        model_admin = PolygonAdmin(Polygon, AdminSite())
        self.assertEqual(
            model_admin.boundary_summary(Polygon()),
            '(no boundary saved yet)',
        )


class PolygonNameRulesTest(TestCase):
    def _form(self, name, display_name=''):
        return PolygonForm(data={
            'name': name,
            'display_name': display_name,
            'description': 'Name rule test.',
            'geojson_text': SQUARE_GEOJSON,
        })

    def test_identifier_style_names_are_accepted(self):
        for name in ('delhi_ncr', 'DelhiNCR', '_private', 'zone2'):
            form = self._form(name)
            self.assertTrue(form.is_valid(), (name, form.errors))
            form.save()

    def test_invalid_names_are_rejected(self):
        for name in ('has spaces', '2starts_with_digit', 'hyphen-ated',
                     'dotted.name', ''):
            form = self._form(name)
            self.assertFalse(form.is_valid(), name)
            self.assertIn('name', form.errors)

    def test_duplicate_name_shows_form_error(self):
        first = self._form('delhi_ncr')
        self.assertTrue(first.is_valid(), first.errors)
        first.save()

        duplicate = self._form('delhi_ncr')

        self.assertFalse(duplicate.is_valid())
        self.assertIn('name', duplicate.errors)
        self.assertIn('already exists', str(duplicate.errors['name']))

    def test_display_name_is_optional_and_saved(self):
        unnamed = self._form('no_display').save()
        named = self._form(
            'with_display', display_name='Delhi NCR'
        ).save()

        self.assertEqual(unnamed.display_name, '')
        self.assertEqual(named.display_name, 'Delhi NCR')

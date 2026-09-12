import json

from django.contrib.admin.sites import AdminSite
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from api.models.polygon_admin import (
    PolygonAdmin,
    PolygonForm,
)
from api.models import Polygon

SQUARE_GEOJSON = json.dumps({
    'type': 'Polygon',
    'coordinates': [[[0, 0], [0, 10], [10, 10], [10, 0], [0, 0]]],
})


class PolygonFormTest(TestCase):
    """Tests for the admin form that creates polygons from GeoJSON."""
    def test_requires_a_geometry_on_create(self):
        """A brand-new polygon must be given a boundary."""
        form = PolygonForm(data={
            'name': 'no_shape',
            'description': 'Missing a boundary.',
        })
        self.assertFalse(form.is_valid())

    def test_description_is_required(self):
        """A polygon cannot be saved without a description — every
        boundary must say what it represents and where it came from."""
        form = PolygonForm(data={
            'name': 'undescribed_boundary',
            'description': '',
            'geojson_text': SQUARE_GEOJSON,
        })
        self.assertFalse(form.is_valid())
        self.assertIn('description', form.errors)

    def test_rejects_invalid_geojson(self):
        """Bad GeoJSON becomes a form error, not an exception."""
        form = PolygonForm(data={
            'name': 'bad_shape',
            'description': 'Has malformed GeoJSON.',
            'geojson_text': 'not json',
        })
        self.assertFalse(form.is_valid())

    def test_accepts_pasted_geojson_text(self):
        """Pasted GeoJSON text saves as geometry."""
        form = PolygonForm(data={
            'name': 'pasted_square',
            'description': 'A square pasted as text.',
            'geojson_text': SQUARE_GEOJSON,
        })
        self.assertTrue(form.is_valid(), form.errors)
        instance = form.save()
        self.assertEqual(instance.geom.geom_type, 'MultiPolygon')

    def test_accepts_uploaded_geojson_file(self):
        """An uploaded GeoJSON file saves as geometry."""
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


class PolygonAdminDisplayTest(TestCase):
    """Tests for how a saved boundary is shown back to staff."""
    def _make_polygon(self):
        """Create a saved polygon through the admin form."""
        form = PolygonForm(data={
            'name': 'display_square',
            'description': 'A square for display tests.',
            'geojson_text': SQUARE_GEOJSON,
        })
        self.assertTrue(form.is_valid(), form.errors)
        return form.save()

    def test_edit_form_prefills_saved_geojson(self):
        """Editing shows the saved GeoJSON, which round-trips unchanged."""
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
        """The summary reports parts, vertices, and extent."""
        polygon = self._make_polygon()
        model_admin = PolygonAdmin(Polygon, AdminSite())

        summary = model_admin.boundary_summary(polygon)

        self.assertIn('1 part(s)', summary)
        self.assertIn('0 hole(s)', summary)
        self.assertIn('5 vertices', summary)
        self.assertIn('0.000, 0.000, 10.000, 10.000', summary)

    def test_boundary_summary_counts_holes(self):
        """Holes are counted so staff can spot both deliberate
        enclaves and accidental sliver gaps at a glance."""
        holed = json.dumps({
            'type': 'Polygon',
            'coordinates': [
                [[0, 0], [0, 10], [10, 10], [10, 0], [0, 0]],
                [[2, 2], [2, 4], [4, 4], [4, 2], [2, 2]],
            ],
        })
        form = PolygonForm(data={
            'name': 'holed_square',
            'description': 'A square with a hole.',
            'geojson_text': holed,
        })
        self.assertTrue(form.is_valid(), form.errors)
        polygon = form.save()
        model_admin = PolygonAdmin(Polygon, AdminSite())

        self.assertIn('1 hole(s)', model_admin.boundary_summary(polygon))

    def test_boundary_summary_handles_unsaved_polygon(self):
        """The summary has a safe fallback before a boundary exists."""
        model_admin = PolygonAdmin(Polygon, AdminSite())
        self.assertEqual(
            model_admin.boundary_summary(Polygon()),
            '(no boundary saved yet)',
        )


class PolygonNameRulesTest(TestCase):
    """Tests for the name rules and the optional display name."""
    def _form(self, name, display_name=''):
        """Build a valid form for the given name and display name."""
        return PolygonForm(data={
            'name': name,
            'display_name': display_name,
            'description': 'Name rule test.',
            'geojson_text': SQUARE_GEOJSON,
        })

    def test_identifier_style_names_are_accepted(self):
        """Underscore, CamelCase, and similar identifier names all pass."""
        for name in ('delhi_ncr', 'DelhiNCR', '_private', 'zone2'):
            form = self._form(name)
            self.assertTrue(form.is_valid(), (name, form.errors))
            form.save()

    def test_invalid_names_are_rejected(self):
        """Spaces, leading digits, hyphens, dots, and blanks are refused."""
        for name in ('has spaces', '2starts_with_digit', 'hyphen-ated',
                     'dotted.name', ''):
            form = self._form(name)
            self.assertFalse(form.is_valid(), name)
            self.assertIn('name', form.errors)

    def test_duplicate_name_shows_form_error(self):
        """A duplicate name surfaces as a form error, pre-database."""
        first = self._form('delhi_ncr')
        self.assertTrue(first.is_valid(), first.errors)
        first.save()

        duplicate = self._form('delhi_ncr')

        self.assertFalse(duplicate.is_valid())
        self.assertIn('name', duplicate.errors)
        self.assertIn('already exists', str(duplicate.errors['name']))

    def test_display_name_is_optional_and_saved(self):
        """display_name may be blank and is stored when given."""
        unnamed = self._form('no_display').save()
        named = self._form(
            'with_display', display_name='Delhi NCR'
        ).save()

        self.assertEqual(unnamed.display_name, '')
        self.assertEqual(named.display_name, 'Delhi NCR')

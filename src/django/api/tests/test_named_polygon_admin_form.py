import json

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from api.admin import NamedPolygonForm

SQUARE_GEOJSON = json.dumps({
    'type': 'Polygon',
    'coordinates': [[[0, 0], [0, 10], [10, 10], [10, 0], [0, 0]]],
})


class NamedPolygonFormTest(TestCase):
    def test_requires_a_geometry_on_create(self):
        form = NamedPolygonForm(data={
            'name': 'No shape',
            'description': 'Missing a boundary.',
        })
        self.assertFalse(form.is_valid())

    def test_rejects_invalid_geojson(self):
        form = NamedPolygonForm(data={
            'name': 'Bad shape',
            'description': 'Has malformed GeoJSON.',
            'geojson_text': 'not json',
        })
        self.assertFalse(form.is_valid())

    def test_accepts_pasted_geojson_text(self):
        form = NamedPolygonForm(data={
            'name': 'Pasted square',
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
        form = NamedPolygonForm(
            data={
                'name': 'Uploaded square',
                'description': 'A square uploaded as a file.',
            },
            files={'geojson_file': upload},
        )
        self.assertTrue(form.is_valid(), form.errors)
        instance = form.save()
        self.assertEqual(instance.geom.geom_type, 'MultiPolygon')

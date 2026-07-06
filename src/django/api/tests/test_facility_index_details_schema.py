from django.test import TestCase
from rest_framework.serializers import SerializerMethodField

from api.serializers import FacilityIndexDetailsSerializer


class FacilityIndexDetailsSchemaTest(TestCase):
    """Drift guard for the ``GET /api/facilities/{id}/`` API documentation.

    Every ``SerializerMethodField`` on the facility detail response returns a
    shape that ``drf-yasg`` cannot introspect on its own. To keep the generated
    Swagger/OpenAPI schema in sync with the code, each such field must declare
    its shape via ``@swagger_serializer_method``. If a new method field is
    added without an annotation, this test fails so the schema is not left
    undocumented.
    """

    def test_all_method_fields_declare_a_swagger_schema(self):
        serializer = FacilityIndexDetailsSerializer()
        geo_field = serializer.Meta.geo_field

        missing = []
        for name, field in serializer.fields.items():
            # The GeoJSON geometry field is documented by the
            # GeoFeatureModelSerializer inspector, not a serializer method.
            if name == geo_field:
                continue
            if not isinstance(field, SerializerMethodField):
                continue

            method_name = field.method_name or 'get_{}'.format(name)
            method = getattr(serializer, method_name, None)
            if getattr(method, '_swagger_serializer', None) is None:
                missing.append(name)

        self.assertEqual(
            missing,
            [],
            'The following SerializerMethodField(s) on '
            'FacilityIndexDetailsSerializer are missing a '
            '@swagger_serializer_method annotation and would be undocumented '
            'in the API docs: {}. Add a typed schema serializer for each and '
            'annotate the getter.'.format(missing),
        )

import json

from django.test import TestCase

from api.models import PartnerField, ZoneSet
from api.models.partner_field_admin import PartnerFieldAdminForm
from api.tests.test_zone_set_provider import zone_pieces
from api.tests.zone_fixtures import feature

LEFT = [[[0, 0], [0, 10], [5, 10], [5, 0], [0, 0]]]
RIGHT = [[[5, 0], [5, 10], [10, 10], [10, 0], [5, 0]]]

SCHEMA = {
    'type': 'object',
    'properties': {
        'bws_label': {'type': 'string', 'title': 'Water stress, today'},
        'bwd_label': {'type': 'string', 'title': 'Drought risk'},
        'atlas_url': {'type': 'string', 'format': 'uri'},
    },
    'required': ['bws_label', 'bwd_label'],
}

WEST = {'bws_label': 'High', 'bwd_label': 'Low', 'pfaf_id': 1,
        'note': 'basin 1'}
EAST = {'bws_label': 'Low', 'bwd_label': 'Low', 'pfaf_id': 2, 'note': ''}


def with_required(schema, *keys, **properties):
    """A copy of `schema` with extra properties and required keys."""
    return {
        **schema,
        'properties': {**schema['properties'], **properties},
        'required': [*schema['required'], *keys],
    }


class PartnerFieldAdminFormZoneSetTest(TestCase):
    """
    Editing a partner field that a zone set with zones feeds: the
    stored zones were read for the field as it was, so a type change
    is refused and a schema change must be one the zones can serve.
    """

    def setUp(self):
        self.field = PartnerField.objects.create(
            name='aqueduct_water_risk', type=PartnerField.OBJECT,
            label='Water risk', json_schema=SCHEMA,
        )
        self.zone_set = ZoneSet.objects.create(
            name='water_risk', partner_field=self.field,
            value_property=None,
        )
        self.zone_set.replace_zones(zone_pieces(
            feature(LEFT, WEST), feature(RIGHT, EAST), schema=SCHEMA,
        ))

    def _form(self, field=None, **changes):
        field = field or self.field
        data = {
            'name': field.name,
            'type': field.type,
            'label': field.label,
            'json_schema': json.dumps(field.json_schema or {}),
            'active': 'on',
            'available_in_api': 'on',
            'available_in_data_downloads': 'on',
        }
        for key, value in changes.items():
            data[key] = json.dumps(value) if key == 'json_schema' else value
        return PartnerFieldAdminForm(data=data, instance=field)

    def test_required_key_every_feature_carries_is_accepted(self):
        form = self._form(json_schema=with_required(
            SCHEMA, 'pfaf_id', pfaf_id={'type': 'integer'},
        ))
        self.assertTrue(form.is_valid(), form.errors)

    def test_required_key_a_feature_lacks_is_refused_with_a_count(self):
        form = self._form(json_schema=with_required(
            SCHEMA, 'drr_label', drr_label={'type': 'string'},
        ))
        self.assertFalse(form.is_valid())
        message = str(form.errors['json_schema'])
        self.assertIn('2 of 2 zone(s) have no value for the required '
                      'property &quot;drr_label&quot;', message)
        self.assertIn('Upload a file that carries the property', message)

    def test_blank_stored_value_counts_as_missing(self):
        """EAST carries `note` as an empty string, which the provider
        would not serve, so requiring it is refused for that feature."""
        form = self._form(json_schema=with_required(
            SCHEMA, 'note', note={'type': 'string'},
        ))
        self.assertFalse(form.is_valid())
        self.assertIn('1 of 2 zone(s) have no value for the required '
                      'property &quot;note&quot;',
                      str(form.errors['json_schema']))

    def test_every_failing_required_key_is_reported_at_once(self):
        form = self._form(json_schema=with_required(
            SCHEMA, 'drr_label', 'note',
            drr_label={'type': 'string'}, note={'type': 'string'},
        ))
        self.assertFalse(form.is_valid())
        message = str(form.errors['json_schema'])
        self.assertIn('&quot;drr_label&quot;', message)
        self.assertIn('&quot;note&quot;', message)

    def test_optional_property_title_and_format_edits_are_accepted(self):
        schema = {
            **SCHEMA,
            'properties': {
                **SCHEMA['properties'],
                'bws_label': {'type': 'string', 'title': 'Water stress'},
                'drr_label': {'type': 'string', 'title': 'Drought'},
                'atlas_url': {'type': 'string', 'format': 'uri',
                              'text': 'Atlas'},
            },
        }
        form = self._form(json_schema=schema)
        self.assertTrue(form.is_valid(), form.errors)

    def test_dropping_a_required_property_is_accepted(self):
        schema = {
            **SCHEMA,
            'properties': {'bws_label': SCHEMA['properties']['bws_label']},
            'required': ['bws_label'],
        }
        form = self._form(json_schema=schema)
        self.assertTrue(form.is_valid(), form.errors)

    def test_schema_without_properties_is_refused_while_linked(self):
        for schema in ({}, {'type': 'object'}, {'properties': {}}):
            with self.subTest(schema=schema):
                form = self._form(json_schema=schema)
                self.assertFalse(form.is_valid())
                self.assertIn('needs a JSON schema with a '
                              '&quot;properties&quot; map',
                              str(form.errors['json_schema']))

    def test_type_change_is_refused_while_the_set_has_zones(self):
        form = self._form(type=PartnerField.STRING)
        self.assertFalse(form.is_valid())
        message = str(form.errors['type'])
        self.assertIn('feeds zone set &quot;water_risk&quot;', message)
        self.assertIn('2 zone(s) were read for a &quot;object&quot; field',
                      message)
        self.assertNotIn('json_schema', form.errors)

    def test_string_field_type_change_is_refused_too(self):
        field = PartnerField.objects.create(
            name='water_stress', type=PartnerField.STRING, label='Stress',
        )
        zone_set = ZoneSet.objects.create(
            name='water_stress', partner_field=field,
            value_property='bws_label',
        )
        zone_set.replace_zones(zone_pieces(feature(LEFT, WEST)))
        form = self._form(field, type=PartnerField.OBJECT,
                          json_schema=SCHEMA)
        self.assertFalse(form.is_valid())
        self.assertIn('read for a &quot;string&quot; field',
                      str(form.errors['type']))

    def test_other_edits_to_a_linked_field_are_not_checked(self):
        form = self._form(label='WRI Aqueduct 4.0 Water Risk',
                          display_text='Aqueduct')
        self.assertTrue(form.is_valid(), form.errors)

    def test_linked_set_without_zones_allows_any_schema(self):
        self.zone_set.zones.all().delete()
        form = self._form(json_schema=with_required(
            SCHEMA, 'drr_label', drr_label={'type': 'string'},
        ))
        self.assertTrue(form.is_valid(), form.errors)

    def test_unlinked_object_field_is_not_checked(self):
        field = PartnerField.objects.create(
            name='free_object', type=PartnerField.OBJECT, label='Free',
            json_schema=SCHEMA,
        )
        form = self._form(field, type=PartnerField.STRING, json_schema={})
        self.assertTrue(form.is_valid(), form.errors)

    def test_new_field_is_not_checked(self):
        form = PartnerFieldAdminForm(data={
            'name': 'brand_new', 'type': PartnerField.OBJECT,
            'label': 'New', 'json_schema': json.dumps(SCHEMA),
            'active': 'on', 'available_in_api': 'on',
            'available_in_data_downloads': 'on',
        })
        self.assertTrue(form.is_valid(), form.errors)

    def test_features_lacking_counts_features_not_pieces(self):
        self.assertEqual(self.zone_set.feature_count, 2)
        self.assertEqual(self.zone_set.features_lacking('bws_label'), 0)
        self.assertEqual(self.zone_set.features_lacking('note'), 1)
        self.assertEqual(self.zone_set.features_lacking('drr_label'), 2)

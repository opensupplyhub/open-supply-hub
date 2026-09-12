from django.db import migrations


FIELD_NAME = 'india_labour_line_helpline'
POLYGON_NAME = 'india_labour_line_helpline_areas'
HELPLINE_NUMBER = '1-800-833-9020'

JSON_SCHEMA = {
    'type': 'object',
    'title': 'India Labour Line Helpline',
    '$schema': 'https://json-schema.org/draft/2020-12/schema',
    'properties': {
        'phone_number': {
            'type': 'string',
            'title': 'Phone Number',
        }
    },
}


def create_or_adopt_partner_field(apps, schema_editor):
    """
    Create the india_labour_line_helpline partner field, or adopt the
    manually-created production row.

    Production already has this field (it was created by hand in the
    admin), so instead of deleting and recreating it — which would
    break its contributor assignment — this migration finds it by name
    and normalizes it to the canonical, code-managed configuration:
    a protected system field (mirroring mit_living_wage) with the
    helpline number in display_text, where staff can still edit it.

    If a Polygon named for the helpline coverage area already exists,
    it is linked; otherwise the link is left empty for staff to set in
    the admin once the boundary is uploaded.
    """
    partner_field_model = apps.get_model('api', 'PartnerField')
    polygon_model = apps.get_model('api', 'Polygon')

    field, _ = partner_field_model.objects.get_or_create(
        name=FIELD_NAME,
        defaults={'type': 'object'},
    )
    field.type = 'object'
    field.label = 'India Labour Line Helpline'
    field.json_schema = JSON_SCHEMA
    field.display_text = HELPLINE_NUMBER
    field.system_field = True
    field.active = True
    if field.polygon_id is None:
        field.polygon = polygon_model.objects.filter(
            name=POLYGON_NAME
        ).first()
    field.save()


def unprotect_partner_field(apps, schema_editor):
    """
    On rollback, release the field rather than deleting it.

    The row may predate this migration (production's was created by
    hand), so deleting it on rollback could destroy configuration this
    migration never created. Clearing system_field returns it to a
    plain, admin-managed field.
    """
    partner_field_model = apps.get_model('api', 'PartnerField')
    partner_field_model.objects.filter(name=FIELD_NAME).update(
        system_field=False, polygon=None,
    )


class Migration(migrations.Migration):
    """Create or adopt the India Labour Line helpline partner field."""

    dependencies = [
        ('api', '0229_add_partner_field_polygon_link'),
    ]

    operations = [
        migrations.RunPython(
            create_or_adopt_partner_field,
            unprotect_partner_field,
        ),
    ]

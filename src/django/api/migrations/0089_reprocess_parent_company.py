from django.db import migrations
from api.extended_fields import (get_parent_company_extendedfield_value)


def process_parent_company_field(apps, schema_editor): 
    ExtendedField = apps.get_model('api', 'ExtendedField')
    extended_fields = ExtendedField.objects.filter(field_name='parent_company')
    for extended_field in extended_fields.iterator():
        raw_parent_company_value = getattr(extended_field, 'value')['raw_value']
        parent_company_value = get_parent_company_extendedfield_value(
                    raw_parent_company_value
                )
        extended_field.value = parent_company_value
        extended_field.save()


def do_nothing_on_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0088_migrate_claim_fields'),
    ]

    operations = [
        migrations.RunPython(process_parent_company_field, do_nothing_on_reverse),
    ]

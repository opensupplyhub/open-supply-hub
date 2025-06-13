import uuid
from django.db import connection
from django.db import migrations, models

from api.migrations._migration_helper import MigrationHelper

helper = MigrationHelper(connection)


def drop_triggers(apps, schema_editor):
    helper.run_sql_files(['0170_drop_table_triggers.sql'])


def create_triggers(apps, schema_editor):
    helper.run_sql_files(['0170_create_table_triggers.sql'])


def add_uuid_field(model_name, help_text):
    """
    Adds a UUID field to the specified model and populates it with random UUIDs
    for existing records. The field is then altered to be non-nullable and
    unique, with a default value set to generate random UUIDs for new records.
    """
    return [
        migrations.AddField(
            model_name=model_name,
            name='uuid',
            field=models.UUIDField(
                null=True,
                editable=False,
                help_text=help_text,
            ),
        ),
        migrations.RunSQL(
            sql=f"""
                UPDATE api_{model_name}
                SET uuid = gen_random_uuid()
                WHERE uuid IS NULL;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.AlterField(
            model_name=model_name,
            name='uuid',
            field=models.UUIDField(
                null=False,
                default=uuid.uuid4,
                unique=True,
                editable=False,
                help_text=help_text,
            ),
        ),
        migrations.RunSQL(
            sql=f"""
                ALTER TABLE api_{model_name}
                ALTER COLUMN uuid
                SET DEFAULT gen_random_uuid();
            """,
            reverse_sql=f"""
                ALTER TABLE api_{model_name}
                ALTER COLUMN uuid
                DROP DEFAULT;
            """,
        ),
    ]


class Migration(migrations.Migration):
    dependencies = [
        ('api', '0169_introduce_show_additional_identifiers_switch'),
    ]

    operations = [
        # Drops triggers.
        migrations.RunPython(
            code=drop_triggers,
            reverse_code=create_triggers,
        ),
        # Adds UUID fields to relevant models.
        *add_uuid_field(
            'contributor',
            'Unique identifier for the contributor.'
        ),
        *add_uuid_field(
            'extendedfield',
            'Unique identifier for the extended field.'
        ),
        *add_uuid_field(
            'facility',
            'Unique identifier for the facility.'
        ),
        *add_uuid_field(
            'facilityactivityreport',
            'Unique identifier for the facility activity report.'
        ),
        *add_uuid_field(
            'facilityalias',
            'Unique identifier for the facility alias.'
        ),
        *add_uuid_field(
            'facilityclaim',
            'Unique identifier for the facility claim.'
        ),
        *add_uuid_field(
            'facilityindex',
            'Unique identifier for the facility index.'
        ),
        *add_uuid_field(
            'facilitylist',
            'Unique identifier for the facility list.'
        ),
        *add_uuid_field(
            'facilitylistitem',
            'Unique identifier for the facility list item.'
        ),
        *add_uuid_field(
            'facilitylocation',
            'Unique identifier for the facility location change.'
        ),
        *add_uuid_field(
            'facilitymatch',
            'Unique identifier for the facility match.'
        ),
        *add_uuid_field(
            'source',
            'Unique identifier for the source.'
        ),
        *add_uuid_field(
            'user',
            'Unique identifier for the user.'
        ),
        # Recreate table triggers.
        migrations.RunPython(
            code=create_triggers,
            reverse_code=drop_triggers,
        ),
    ]

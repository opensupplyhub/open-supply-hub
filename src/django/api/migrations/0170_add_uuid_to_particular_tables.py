import uuid
from django.db import connection
from django.db import migrations, models

from api.migrations._migration_helper import MigrationHelper

helper = MigrationHelper(connection)


def drop_triggers(apps, schema_editor):
    print("→ starting to drop table triggers…")
    helper.run_sql_files(['table_triggers/drop_table_triggers.sql'])
    print("✓ table triggers dropped successfully")


def create_triggers(apps, schema_editor):
    print("→ starting to create table triggers…")
    helper.run_sql_files(['table_triggers/create_table_triggers.sql'])
    print("✓ table triggers created successfully")


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
        # Adds a UUID field to the Source model.
        migrations.AddField(
            model_name='source',
            name='uuid',
            field=models.UUIDField(
                null=True,
                editable=False,
                help_text='Unique identifier for the source.',
            ),
        ),
        migrations.RunPython(
            code=lambda apps, schema_editor: print(
                "→ starting SQL back-fill of uuid…"
            ),
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.RunSQL(
            sql="""
                UPDATE api_source
                SET uuid = gen_random_uuid()
                WHERE uuid IS NULL;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.RunPython(
            code=lambda apps, schema_editor: print("✓ SQL back-fill complete"),
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name='source',
            name='uuid',
            field=models.UUIDField(
                null=False,
                default=uuid.uuid4,
                unique=True,
                editable=False,
                help_text='Unique identifier for the source.',
            ),
        ),
        # Adds a UUID field to the Contributor model.
        migrations.AddField(
            model_name='contributor',
            name='uuid',
            field=models.UUIDField(
                null=True,
                editable=False,
                help_text='Unique identifier for the contributor.',
            ),
        ),
        migrations.RunPython(
            code=lambda apps, schema_editor: print(
                "→ starting SQL back-fill of contributor uuid…"
            ),
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.RunSQL(
            sql="""
                UPDATE api_contributor
                SET uuid = gen_random_uuid()
                WHERE uuid IS NULL;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.RunPython(
            code=lambda apps, schema_editor: print("✓ SQL back-fill complete"),
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name='contributor',
            name='uuid',
            field=models.UUIDField(
                null=False,
                default=uuid.uuid4,
                unique=True,
                editable=False,
                help_text='Unique identifier for the contributor.',
            ),
        ),
        # Adds a UUID field to the ExtendedField model.
        migrations.AddField(
            model_name='extendedfield',
            name='uuid',
            field=models.UUIDField(
                null=True,
                editable=False,
                help_text='Unique identifier for the extended field.',
            ),
        ),
        migrations.RunPython(
            code=lambda apps, schema_editor: print(
                "→ starting SQL back-fill of extended field uuid…"
            ),
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.RunSQL(
            sql="""
                UPDATE api_extendedfield
                SET uuid = gen_random_uuid()
                WHERE uuid IS NULL;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.RunPython(
            code=lambda apps, schema_editor: print("✓ SQL back-fill complete"),
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name='extendedfield',
            name='uuid',
            field=models.UUIDField(
                null=False,
                default=uuid.uuid4,
                unique=True,
                editable=False,
                help_text='Unique identifier for the extended field.',
            ),
        ),

    ]

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

        # Adds a UUID field to the Source model and updates the FacilityListItem model to reference this UUID.
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

        migrations.AddField(
            model_name='facilitylistitem',
            name='source_uuid',
            field=models.ForeignKey(
                to='api.source',
                to_field='uuid',
                db_column='source_uuid',
                on_delete=models.PROTECT,
                null=True,
                editable=False,
                related_name='facility_list_items',
                help_text='The UUID of the source from which this item was created.',
            ),
        ),
        migrations.RunSQL(
            sql="""
                UPDATE api_facilitylistitem AS fli
                SET source_uuid = s.uuid
                FROM api_source AS s
                WHERE fli.source_id = s.id;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.AlterField(
            model_name='facilitylistitem',
            name='source_uuid',
            field=models.ForeignKey(
                to='api.source',
                to_field='uuid',
                db_column='source_uuid',
                on_delete=models.PROTECT,
                null=False,
                editable=False,
                related_name='facility_list_items',
                help_text='The UUID of the source from which this item was created.',
            ),
        ),

        # Recreate triggers.
        migrations.RunPython(
            code=create_triggers,
            reverse_code=drop_triggers,
        ),
    ]

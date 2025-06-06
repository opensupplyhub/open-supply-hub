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
        # Adds a UUID field to the Facility model.
        migrations.AddField(
            model_name='facility',
            name='uuid',
            field=models.UUIDField(
                null=True,
                editable=False,
                help_text='Unique identifier for the facility.',
            ),
        ),
        migrations.RunPython(
            code=lambda apps, schema_editor: print(
                "→ starting SQL back-fill of facility uuid…"
            ),
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.RunSQL(
            sql="""
                UPDATE api_facility
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
            model_name='facility',
            name='uuid',
            field=models.UUIDField(
                null=False,
                default=uuid.uuid4,
                unique=True,
                editable=False,
                help_text='Unique identifier for the facility.',
            ),
        ),
        # Adds a UUID field to the FacilityActivityReport model.
        migrations.AddField(
            model_name='facilityactivityreport',
            name='uuid',
            field=models.UUIDField(
                null=True,  
                editable=False,
                help_text='Unique identifier for the facility activity report.',
            ),
        ),
        migrations.RunPython(
            code=lambda apps, schema_editor: print(
                "→ starting SQL back-fill of facility activity report uuid…"
            ),
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.RunSQL(
            sql="""
                UPDATE api_facilityactivityreport
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
            model_name='facilityactivityreport',
            name='uuid',
            field=models.UUIDField(
                null=False,
                default=uuid.uuid4,
                unique=True,
                editable=False,
                help_text='Unique identifier for the facility activity report.',
            ),
        ),
        # Adds a UUID field to the FacilityAlias model.
        migrations.AddField(
            model_name='facilityalias',
            name='uuid',
            field=models.UUIDField(
                null=True,
                editable=False,
                help_text='Unique identifier for the facility alias.',
            ),
        ),
        migrations.RunPython(
            code=lambda apps, schema_editor: print(
                "→ starting SQL back-fill of facility alias uuid…"
            ),
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.RunSQL(
            sql="""
                UPDATE api_facilityalias
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
            model_name='facilityalias',
            name='uuid',
            field=models.UUIDField(
                null=False,
                default=uuid.uuid4,
                unique=True,
                editable=False,
                help_text='Unique identifier for the facility alias.',
            ),
        ),
        # Adds a UUID field to the FacilityClaim model.
        migrations.AddField(
            model_name='facilityclaim',
            name='uuid',
            field=models.UUIDField(
                null=True,
                editable=False,
                help_text='Unique identifier for the facility claim.',
            ),
        ),
        migrations.RunPython(
            code=lambda apps, schema_editor: print(
                "→ starting SQL back-fill of facility claim uuid…"
            ),
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.RunSQL(
            sql="""
                UPDATE api_facilityclaim
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
            model_name='facilityclaim',
            name='uuid',
            field=models.UUIDField(
                null=False,
                default=uuid.uuid4,
                unique=True,
                editable=False,
                help_text='Unique identifier for the facility claim.',
            ),
        ),
        # Adds a UUID field to the FacilityList model.
        migrations.AddField(
            model_name='facilitylist',
            name='uuid',
            field=models.UUIDField(
                null=True,
                editable=False,
                help_text='Unique identifier for the facility list.',
            ),
        ),
        migrations.RunPython(
            code=lambda apps, schema_editor: print(
                "→ starting SQL back-fill of facility list uuid…"
            ),
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.RunSQL(
            sql="""
                UPDATE api_facilitylist
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
            model_name='facilitylist',
            name='uuid',
            field=models.UUIDField(
                null=False,
                default=uuid.uuid4,
                unique=True,
                editable=False,
                help_text='Unique identifier for the facility list.',
            ),
        ), 
    ]

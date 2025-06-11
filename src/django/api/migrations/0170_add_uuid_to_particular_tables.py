import uuid
from django.db import connection
from django.db import migrations, models

from api.migrations._migration_helper import MigrationHelper

helper = MigrationHelper(connection)


def drop_triggers(apps, schema_editor):
    helper.run_sql_files(['0170_drop_table_triggers.sql'])


def create_triggers(apps, schema_editor):
    helper.run_sql_files(['0170_create_table_triggers.sql'])


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
        migrations.RunSQL(
            sql="""
                UPDATE api_contributor
                SET uuid = gen_random_uuid()
                WHERE uuid IS NULL;
            """,
            reverse_sql=migrations.RunSQL.noop,
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
        migrations.RunSQL(
            sql="""
                ALTER TABLE api_contributor
                    ALTER COLUMN uuid
                    SET DEFAULT gen_random_uuid();
            """,
            reverse_sql="""
                ALTER TABLE api_contributor
                    ALTER COLUMN uuid
                    DROP DEFAULT;
            """,
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
        migrations.RunSQL(
            sql="""
                UPDATE api_extendedfield
                SET uuid = gen_random_uuid()
                WHERE uuid IS NULL;
            """,
            reverse_sql=migrations.RunSQL.noop,
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
        migrations.RunSQL(
            sql="""
                ALTER TABLE api_extendedfield
                    ALTER COLUMN uuid
                    SET DEFAULT gen_random_uuid();
            """,
            reverse_sql="""
                ALTER TABLE api_extendedfield
                    ALTER COLUMN uuid
                    DROP DEFAULT;
            """,
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
        migrations.RunSQL(
            sql="""
                UPDATE api_facility
                SET uuid = gen_random_uuid()
                WHERE uuid IS NULL;
            """,
            reverse_sql=migrations.RunSQL.noop,
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
        migrations.RunSQL(
            sql="""
                ALTER TABLE api_facility
                    ALTER COLUMN uuid
                    SET DEFAULT gen_random_uuid();
            """,
            reverse_sql="""
                ALTER TABLE api_facility
                    ALTER COLUMN uuid
                    DROP DEFAULT;
            """,
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
        migrations.RunSQL(
            sql="""
                UPDATE api_facilityactivityreport
                SET uuid = gen_random_uuid()
                WHERE uuid IS NULL;
            """,
            reverse_sql=migrations.RunSQL.noop,
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
        migrations.RunSQL(
            sql="""
                ALTER TABLE api_facilityactivityreport
                    ALTER COLUMN uuid
                    SET DEFAULT gen_random_uuid();
            """,
            reverse_sql="""
                ALTER TABLE api_facilityactivityreport
                    ALTER COLUMN uuid
                    DROP DEFAULT;
            """,
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
        migrations.RunSQL(
            sql="""
                UPDATE api_facilityalias
                SET uuid = gen_random_uuid()
                WHERE uuid IS NULL;
            """,
            reverse_sql=migrations.RunSQL.noop,
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
        migrations.RunSQL(
            sql="""
                ALTER TABLE api_facilityalias
                    ALTER COLUMN uuid
                    SET DEFAULT gen_random_uuid();
            """,
            reverse_sql="""
                ALTER TABLE api_facilityalias
                    ALTER COLUMN uuid
                    DROP DEFAULT;
            """,
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
        migrations.RunSQL(
            sql="""
                UPDATE api_facilityclaim
                SET uuid = gen_random_uuid()
                WHERE uuid IS NULL;
            """,
            reverse_sql=migrations.RunSQL.noop,
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
        migrations.RunSQL(
            sql="""
                ALTER TABLE api_facilityclaim
                    ALTER COLUMN uuid
                    SET DEFAULT gen_random_uuid();
            """,
            reverse_sql="""
                ALTER TABLE api_facilityclaim
                    ALTER COLUMN uuid
                    DROP DEFAULT;
            """,
        ),
        # Adds a UUID field to the FacilityIndex model.
        migrations.AddField(
            model_name='facilityindex',
            name='uuid',
            field=models.UUIDField(
                null=True,
                editable=False,
                help_text='Unique identifier for the facility index.',
            ),
        ),
        migrations.RunSQL(
            sql="""
                UPDATE api_facilityindex
                SET uuid = gen_random_uuid()
                WHERE uuid IS NULL;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.AlterField(
            model_name='facilityindex',
            name='uuid',
            field=models.UUIDField(
                null=False,
                default=uuid.uuid4,
                unique=True,
                editable=False,
                help_text='Unique identifier for the facility index.',
            ),  
        ),
        migrations.RunSQL(
            sql="""
                ALTER TABLE api_facilityindex
                    ALTER COLUMN uuid
                    SET DEFAULT gen_random_uuid();
            """,
            reverse_sql="""
                ALTER TABLE api_facilityindex
                    ALTER COLUMN uuid
                    DROP DEFAULT;
            """,
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
        migrations.RunSQL(
            sql="""
                UPDATE api_facilitylist
                SET uuid = gen_random_uuid()
                WHERE uuid IS NULL;
            """,
            reverse_sql=migrations.RunSQL.noop,
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
        migrations.RunSQL(
            sql="""
                ALTER TABLE api_facilitylist
                    ALTER COLUMN uuid
                    SET DEFAULT gen_random_uuid();
            """,
            reverse_sql="""
                ALTER TABLE api_facilitylist
                    ALTER COLUMN uuid   
                    DROP DEFAULT;
            """,
        ),
        # Adds a UUID field to the FacilityListItem model.
        migrations.AddField(
            model_name='facilitylistitem',
            name='uuid',
            field=models.UUIDField(
                null=True,
                editable=False,
                help_text='Unique identifier for the facility list item.',
            ),
        ),
        migrations.RunSQL(
            sql="""
                UPDATE api_facilitylistitem
                SET uuid = gen_random_uuid()
                WHERE uuid IS NULL;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.AlterField(
            model_name='facilitylistitem',
            name='uuid',
            field=models.UUIDField(
                null=False,
                default=uuid.uuid4,
                unique=True,
                editable=False,
                help_text='Unique identifier for the facility list item.',
            ),
        ),
        migrations.RunSQL(
            sql="""
                ALTER TABLE api_facilitylistitem
                    ALTER COLUMN uuid
                    SET DEFAULT gen_random_uuid();
            """,    
            reverse_sql="""
                ALTER TABLE api_facilitylistitem
                    ALTER COLUMN uuid
                    DROP DEFAULT;
            """,
        ),
        # Adds a UUID field to the FacilityLocation model.
        migrations.AddField(
            model_name='facilitylocation',
            name='uuid',
            field=models.UUIDField(
                null=True,
                editable=False,
                help_text='Unique identifier for the facility location change.',
            ),
        ),
        migrations.RunSQL(
            sql="""
                UPDATE api_facilitylocation
                SET uuid = gen_random_uuid()
                WHERE uuid IS NULL;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.AlterField(
            model_name='facilitylocation',
            name='uuid',
            field=models.UUIDField(
                null=False,
                default=uuid.uuid4,
                unique=True,
                editable=False,
                help_text='Unique identifier for the facility location change.',
            ),
        ),
        migrations.RunSQL(
            sql="""
                ALTER TABLE api_facilitylocation
                    ALTER COLUMN uuid
                    SET DEFAULT gen_random_uuid();
            """,
            reverse_sql="""
                ALTER TABLE api_facilitylocation
                    ALTER COLUMN uuid
                    DROP DEFAULT;
            """,
        ),
        # Adds a UUID field to the FacilityMatch model.
        migrations.AddField(
            model_name='facilitymatch',
            name='uuid',
            field=models.UUIDField(
                null=True,
                editable=False,
                help_text='Unique identifier for the facility match.',
            ),
        ),
        migrations.RunSQL(
            sql="""
                UPDATE api_facilitymatch
                SET uuid = gen_random_uuid()
                WHERE uuid IS NULL;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.AlterField(
            model_name='facilitymatch',
            name='uuid',
            field=models.UUIDField(
                null=False,
                default=uuid.uuid4,
                unique=True,
                editable=False,
                help_text='Unique identifier for the facility match.',
            ),
        ),
        migrations.RunSQL(
            sql="""
                ALTER TABLE api_facilitymatch
                    ALTER COLUMN uuid
                    SET DEFAULT gen_random_uuid();
            """,
            reverse_sql="""
                ALTER TABLE api_facilitymatch
                    ALTER COLUMN uuid
                    DROP DEFAULT;
            """,
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
        migrations.RunSQL(
            sql="""
                UPDATE api_source
                SET uuid = gen_random_uuid()
                WHERE uuid IS NULL;
            """,
            reverse_sql=migrations.RunSQL.noop,
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
        migrations.RunSQL(
            sql="""
                ALTER TABLE api_source
                    ALTER COLUMN uuid
                    SET DEFAULT gen_random_uuid();
            """,
            reverse_sql="""
                ALTER TABLE api_source
                    ALTER COLUMN uuid
                    DROP DEFAULT;
            """,
        ),
        # Add a UUID field to the User model.
        migrations.AddField(
            model_name='user',
            name='uuid',
            field=models.UUIDField(
                null=True,
                editable=False,
                help_text='Unique identifier for the user.',
            ),
        ),
        migrations.RunSQL(
            sql="""
                UPDATE api_user
                SET uuid = gen_random_uuid()
                WHERE uuid IS NULL;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.AlterField(
            model_name='user',
            name='uuid',
            field=models.UUIDField(
                null=False,
                default=uuid.uuid4,
                unique=True,
                editable=False,
                help_text='Unique identifier for the user.',
            ),
        ),
        migrations.RunSQL(
            sql="""
                ALTER TABLE api_user
                    ALTER COLUMN uuid
                    SET DEFAULT gen_random_uuid();
            """,
            reverse_sql="""
                ALTER TABLE api_user
                    ALTER COLUMN uuid
                    DROP DEFAULT;
            """,
        ),
        # Recreate table triggers.
        migrations.RunPython(
            code=create_triggers,
            reverse_code=drop_triggers,
        ),
    ]

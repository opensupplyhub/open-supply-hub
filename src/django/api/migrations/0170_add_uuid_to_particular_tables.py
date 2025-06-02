from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0169_introduce_show_additional_identifiers_switch'),
    ]

    operations = [
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
            reverse_sql="""
                UPDATE api_source
                SET uuid = NULL
                WHERE uuid IS NOT NULL;
            """,
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
                related_name='facility_list_items_by_uuid',
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
            reverse_sql="""
                UPDATE api_facilitylistitem AS fli
                SET source_uuid = NULL
                WHERE fli.source_uuid IS NOT NULL;
            """,
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
                related_name='facility_list_items_by_uuid',
                help_text='The UUID of the source from which this item was created.',
            ),
        ),
    ]

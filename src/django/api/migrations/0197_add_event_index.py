from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0196_switch_partner_field_source_by_editor"),
    ]

    operations = [
        migrations.RunSQL(
            sql=[
                "DROP INDEX IF EXISTS api_event_content_type_id_object_id_idx",
                "DROP INDEX IF EXISTS api_event_content_type_id_object_id_b046420a_idx",
            ],
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.AddIndex(
            model_name="event",
            index=models.Index(
                fields=["content_type", "object_id"],
                name="api_event_content_object_idx",
            ),
        ),
    ]

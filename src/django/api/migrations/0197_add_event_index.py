from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0196_switch_partner_field_source_by_editor"),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name="event",
            name="api_event_content_type_id_object_id_idx",
        ),
        migrations.AddIndex(
            model_name="event",
            index=models.Index(
                fields=["content_type", "object_id"],
                name="api_event_content_object_idx",
            ),
        ),
    ]

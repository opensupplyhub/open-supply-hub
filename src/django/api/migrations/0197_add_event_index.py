from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0196_switch_partner_field_source_by_editor"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="event",
            options={
                "indexes": [
                    models.Index(
                        fields=["content_type", "object_id"],
                        name="api_event_content_object_idx",
                    )
                ]
            },
        ),
    ]


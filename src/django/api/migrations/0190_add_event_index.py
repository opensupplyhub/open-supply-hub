from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0189_add_base_url_and_text_field_to_partner_field"),
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


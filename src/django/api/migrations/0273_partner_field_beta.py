from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Adds `beta` to `api_partnerfield` (OSDEV-3778): when checked, the
    production location page shows a "Beta" tag beside the field's title.
    Defaults to False, so every existing field renders as before.
    """

    dependencies = [
        ('api', '0272_subdivide_existing_zones'),
    ]

    operations = [
        migrations.AddField(
            model_name='partnerfield',
            name='beta',
            field=models.BooleanField(
                default=False,
                help_text=(
                    'Shows a "Beta" tag beside this field\'s title on the '
                    'production location page, for datasets that are still '
                    'provisional. The tag is not part of the label, so '
                    'analytics event names and the contributions drawer '
                    'title are unchanged.'
                ),
            ),
        ),
    ]

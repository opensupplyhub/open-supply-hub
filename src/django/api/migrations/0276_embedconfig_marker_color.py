import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Lets a contributor choose one color for the facility markers on their
    embedded map, separate from the map's primary color. Not set by default,
    so markers keep using the primary color.
    """

    dependencies = [
        ('api', '0275_embedconfig_list_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='embedconfig',
            name='marker_color',
            field=models.CharField(
                blank=True,
                help_text='The color of the facility markers on the '
                          'embedded map when they are not colored by a '
                          'field. The primary color is used when this is '
                          'not set.',
                max_length=7,
                null=True,
                validators=[
                    django.core.validators.RegexValidator(
                        message='Enter a color as a six-digit hex value, '
                                'for example #1386c6.',
                        regex='^#[0-9a-fA-F]{6}$',
                    ),
                ],
            ),
        ),
    ]

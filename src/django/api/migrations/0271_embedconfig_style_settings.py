import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Adds the embedded map style settings a contributor can choose for
    themselves: an accent color, a heading font and a corner radius.

    All three default to "not set" (NULL), which the embedded map treats
    as today's look, so no existing embed changes.
    """

    dependencies = [
        ('api', '0270_claim_campaign_supplier_roster'),
    ]

    operations = [
        migrations.AddField(
            model_name='embedconfig',
            name='accent_color',
            field=models.CharField(
                blank=True,
                help_text='The accent color of the embedded map. The '
                          'primary color is used when this is not set.',
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
        migrations.AddField(
            model_name='embedconfig',
            name='heading_font',
            field=models.CharField(
                blank=True,
                help_text='The font for headings in the embedded map. The '
                          'body font is used when this is not set.',
                max_length=200,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='embedconfig',
            name='corner_radius',
            field=models.PositiveSmallIntegerField(
                blank=True,
                help_text='The corner radius, in pixels, of buttons and '
                          'inputs in the embedded map. Each element keeps '
                          'its own corner style when this is not set.',
                null=True,
                validators=[
                    django.core.validators.MaxValueValidator(16),
                ],
            ),
        ),
    ]

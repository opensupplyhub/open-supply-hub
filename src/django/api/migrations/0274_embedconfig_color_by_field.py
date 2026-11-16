import api.models.embed_config
from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Lets a contributor color the markers on their embedded map by the value
    of one of their fields (a tier, for example). Not set by default, so no
    existing embed changes.
    """

    dependencies = [
        ('api', '0273_embedfield_filterable'),
    ]

    operations = [
        migrations.AddField(
            model_name='embedconfig',
            name='color_by_field',
            field=models.CharField(
                blank=True,
                help_text='The column name of the embed field whose value '
                          'colors each facility marker on the embedded map, '
                          'for example a tier. Markers share one color when '
                          'this is not set.',
                max_length=200,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='embedconfig',
            name='color_by_colors',
            field=models.JSONField(
                blank=True,
                default=dict,
                help_text='The marker color for each value of '
                          'color_by_field, as {value: hex color}.',
                validators=[
                    api.models.embed_config.validate_color_by_colors,
                ],
            ),
        ),
    ]

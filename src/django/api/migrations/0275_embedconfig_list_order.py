import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Lets a contributor choose the order of the facility list on their
    embedded map, and whether visitors can change it. Not set by default, so
    every existing embed keeps its list sorted by name.
    """

    dependencies = [
        ('api', '0274_embedconfig_color_by_field'),
    ]

    operations = [
        migrations.AddField(
            model_name='embedconfig',
            name='default_sort',
            field=models.CharField(
                blank=True,
                help_text='The order of the facility list on the embedded '
                          'map: name_asc, name_desc, field:<column name> or '
                          '-field:<column name> for descending. The list is '
                          'sorted by name when this is not set.',
                max_length=220,
                null=True,
                validators=[
                    django.core.validators.RegexValidator(
                        message='Sort by name_asc, name_desc, '
                                'field:<column> or -field:<column>.',
                        regex='^(name_asc|name_desc|-?field:.+)$',
                    ),
                ],
            ),
        ),
        migrations.AddField(
            model_name='embedconfig',
            name='allow_visitor_sort',
            field=models.BooleanField(
                default=False,
                help_text='Whether visitors to the embedded map can change '
                          'the order of the facility list.',
            ),
        ),
    ]

from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Adds two display options to the fields a contributor shows on their
    embedded map: whether a field also appears in the search results list,
    and whether its value is shown as text, tags or a blurb.

    The defaults (not in the list, shown as text) are how every field is
    displayed today, so no existing embed changes.
    """

    dependencies = [
        ('api', '0271_embedconfig_style_settings'),
    ]

    operations = [
        migrations.AddField(
            model_name='embedfield',
            name='show_in_list',
            field=models.BooleanField(
                default=False,
                help_text='Whether or not to also display this field on '
                          'the facility in the search results list. Only '
                          'applies to visible fields.',
            ),
        ),
        migrations.AddField(
            model_name='embedfield',
            name='display_as',
            field=models.CharField(
                choices=[
                    ('text', 'Text'),
                    ('tags', 'Tags'),
                    ('blurb', 'Blurb'),
                ],
                default='text',
                help_text='How to display the value of this field: as '
                          'plain text, as tags, or as a blurb.',
                max_length=10,
            ),
        ),
    ]

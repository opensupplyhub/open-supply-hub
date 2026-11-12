from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Lets a contributor offer one of their embedded map fields as a filter.
    Off by default, so no existing embed gains a filter.
    """

    dependencies = [
        ('api', '0272_embedfield_display_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='embedfield',
            name='filterable',
            field=models.BooleanField(
                default=False,
                help_text='Whether or not to offer this field as a filter '
                          'on the embedded map. Only applies to visible '
                          'fields.',
            ),
        ),
    ]

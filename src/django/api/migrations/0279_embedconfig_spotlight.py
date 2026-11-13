from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Lets a contributor show Spotlight data, from OS Hub's data partners, on
    their embedded map. All off by default, so no existing embed changes.
    """

    dependencies = [
        ('api', '0278_embedsupplychain'),
    ]

    operations = [
        migrations.AddField(
            model_name='embedconfig',
            name='show_spotlight',
            field=models.BooleanField(
                default=False,
                help_text='Whether the embedded map shows Spotlight data '
                          'from OS Hub data partners.',
            ),
        ),
        migrations.AddField(
            model_name='embedconfig',
            name='spotlight_highlight',
            field=models.BooleanField(
                default=False,
                help_text='Whether facilities that have Spotlight data are '
                          'ringed on the embedded map.',
            ),
        ),
        migrations.AddField(
            model_name='embedconfig',
            name='spotlight_filter',
            field=models.BooleanField(
                default=False,
                help_text='Whether visitors to the embedded map can filter '
                          'by Spotlight data.',
            ),
        ),
        migrations.AddField(
            model_name='embedconfig',
            name='spotlight_groups',
            field=models.JSONField(
                blank=True,
                default=list,
                help_text='The UUIDs of the partner field groups whose '
                          'Spotlight data the embedded map shows.',
            ),
        ),
    ]

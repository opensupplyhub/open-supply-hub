# OSDEV-3726: what the auto-lists-cleaning state machine said about a run
# as a whole (batches, rows the model never judged, degraded), kept apart
# from the prompt's own usage block.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0275_list_cleaning_tour_dismissed'),
    ]

    operations = [
        migrations.AddField(
            model_name='listcleaningrun',
            name='pipeline',
            field=models.JSONField(
                blank=True,
                default=dict,
                help_text='How the state machine ran: execution name, '
                          'batches total and failed, the rows the model '
                          'never judged (model_error_rows), whether the '
                          'report is rules-only for half the list or more '
                          '(degraded), and how many model suggestions '
                          'were rejected by the contract.'),
        ),
    ]

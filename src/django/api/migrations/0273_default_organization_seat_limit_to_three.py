from django.db import migrations, models

SEAT_LIMIT_HELP_TEXT = (
    'The most people the organization can hold: active members plus '
    'invitations still waiting for an answer.'
)


class Migration(migrations.Migration):
    """
    A new organization starts with three seats instead of ten: most
    teams that manage OS Hub are one to three people. Organizations
    that already exist keep the limit they have.
    """

    dependencies = [
        ('api', '0272_show_organization_name_in_facility_index'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='seat_limit',
            field=models.PositiveIntegerField(
                default=3,
                help_text=SEAT_LIMIT_HELP_TEXT,
            ),
        ),
        migrations.AlterField(
            model_name='historicalorganization',
            name='seat_limit',
            field=models.PositiveIntegerField(
                default=3,
                help_text=SEAT_LIMIT_HELP_TEXT,
            ),
        ),
    ]

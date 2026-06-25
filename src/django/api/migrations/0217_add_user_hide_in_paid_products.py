from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0216_backfill_moderation_event_os_id_snapshot'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='hide_in_paid_products',
            field=models.BooleanField(
                default=True,
                help_text=(
                    "When enabled, this contributor's name is hidden "
                    '(anonymized) in OS Hub paid products - the bulk data '
                    'download and the programmatic API - so the data cannot '
                    'be attributed to them at scale. Only takes effect for '
                    'trade union (Union) contributors.'
                ),
                verbose_name='Hide contributor name in paid products',
            ),
        ),
    ]

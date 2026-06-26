from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0217_add_contribution_dates_to_index_contributors'),
    ]

    operations = [
        migrations.AddField(
            model_name='contributor',
            name='anonymise_in_paid_products',
            field=models.BooleanField(
                default=False,
                help_text=(
                    "When enabled, this contributor's name is anonymised in "
                    'OS Hub paid products - the bulk data download and the '
                    'programmatic API - so the data cannot be attributed to '
                    'them at scale. Their contributions stay visible on the '
                    'public web app and facility profiles.'
                ),
                verbose_name='Anonymise contributor name in paid products',
            ),
        ),
        migrations.AddField(
            model_name='historicalcontributor',
            name='anonymise_in_paid_products',
            field=models.BooleanField(
                default=False,
                help_text=(
                    "When enabled, this contributor's name is anonymised in "
                    'OS Hub paid products - the bulk data download and the '
                    'programmatic API - so the data cannot be attributed to '
                    'them at scale. Their contributions stay visible on the '
                    'public web app and facility profiles.'
                ),
                verbose_name='Anonymise contributor name in paid products',
            ),
        ),
    ]

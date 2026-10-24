from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Lets claimants submit ISIC Rev 4 and Rev 5 values with a claim and edit
    them once it is approved (OSDEV-2974). New nullable columns only.
    """

    dependencies = [
        ('api', '0257_index_isic_mapped_search'),
    ]

    operations = [
        migrations.AddField(
            model_name='facilityclaim',
            name='isic_4',
            field=models.JSONField(
                blank=True,
                help_text=(
                    'ISIC Rev 4 values the claimant submitted, each with '
                    'every level filled in.'
                ),
                null=True,
                verbose_name='ISIC Rev. 4',
            ),
        ),
        migrations.AddField(
            model_name='facilityclaim',
            name='isic_5',
            field=models.JSONField(
                blank=True,
                help_text=(
                    'ISIC Rev 5 values the claimant submitted, each with '
                    'every level filled in.'
                ),
                null=True,
                verbose_name='ISIC Rev. 5',
            ),
        ),
        migrations.AddField(
            model_name='historicalfacilityclaim',
            name='isic_4',
            field=models.JSONField(
                blank=True,
                help_text=(
                    'ISIC Rev 4 values the claimant submitted, each with '
                    'every level filled in.'
                ),
                null=True,
                verbose_name='ISIC Rev. 4',
            ),
        ),
        migrations.AddField(
            model_name='historicalfacilityclaim',
            name='isic_5',
            field=models.JSONField(
                blank=True,
                help_text=(
                    'ISIC Rev 5 values the claimant submitted, each with '
                    'every level filled in.'
                ),
                null=True,
                verbose_name='ISIC Rev. 5',
            ),
        ),
    ]

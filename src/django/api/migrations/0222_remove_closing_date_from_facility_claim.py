from django.db import migrations


class Migration(migrations.Migration):
    """
    Drop closing_date from FacilityClaim and HistoricalFacilityClaim.
    See OSDEV-2977.
    """

    dependencies = [
        ('api', '0221_remove_closing_date_from_claim_index_functions'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='facilityclaim',
            name='closing_date',
        ),
        migrations.RemoveField(
            model_name='historicalfacilityclaim',
            name='closing_date',
        ),
    ]

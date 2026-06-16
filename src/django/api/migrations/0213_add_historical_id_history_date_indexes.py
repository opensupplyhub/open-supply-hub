from django.contrib.postgres.operations import AddIndexConcurrently
from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Add composite (id, history_date) indexes to the historical_* tables read
    by the Change Intelligence Phase 1 signal queries (OSDEV-2839), which run
    `LAG(...) OVER (PARTITION BY id ORDER BY history_date)`.

    Without these, the window does a full sort (or seq scan + sort) at
    production scale. Built CONCURRENTLY so the index creation does not lock
    the tables; this requires a non-atomic migration.
    """

    atomic = False

    dependencies = [
        ('api', '0212_add_moderation_pause_info_switch'),
    ]

    operations = [
        AddIndexConcurrently(
            model_name='historicalfacility',
            index=models.Index(
                fields=['id', 'history_date'],
                name='hist_facility_id_histdate_idx',
            ),
        ),
        AddIndexConcurrently(
            model_name='historicalextendedfield',
            index=models.Index(
                fields=['id', 'history_date'],
                name='hist_extfield_id_histdate_idx',
            ),
        ),
        AddIndexConcurrently(
            model_name='historicalfacilityclaim',
            index=models.Index(
                fields=['id', 'history_date'],
                name='hist_claim_id_histdate_idx',
            ),
        ),
    ]

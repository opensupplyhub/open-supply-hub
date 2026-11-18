# OSDEV-3865: keep api_facility planner statistics fresh enough for the
# is_candidate NOT EXISTS guard in FacilityIndexNewManager.without_candidates.
#
# is_candidate was added in 0237 with every row false, so the column
# statistics recorded "no candidates". Candidates (e.g. earth_genome
# satellite detections) are a small fraction of api_facility, so they never
# reached the default re-analyze trigger (50 rows + 10% of the table). The
# planner kept estimating 1 candidate row against ~16k real ones and chose a
# nested-loop anti join that compared every result row with every candidate:
# COUNT(*) for GET /api/facilities/?countries=CN took ~180 s (1.8 billion
# join-filter comparisons) and CloudFront returned 504.
#
# 1. ANALYZE now, so the deploy itself fixes the estimate.
# 2. Re-analyze after a fixed 5,000 row changes. The scale factor is 0 so
#    the trigger doesn't grow with the table: any percentage of ~2.5M rows
#    is larger than the whole candidate population, so candidate writes
#    alone could never trip it.
#
# Both statements take only a SHARE UPDATE EXCLUSIVE lock, which does not
# block reads or writes.

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0284_zone_set_last_upload_sha256'),
    ]

    operations = [
        migrations.RunSQL(
            sql=(
                'ALTER TABLE api_facility SET ('
                'autovacuum_analyze_scale_factor = 0.0, '
                'autovacuum_analyze_threshold = 5000);'
            ),
            reverse_sql=(
                'ALTER TABLE api_facility RESET ('
                'autovacuum_analyze_scale_factor, '
                'autovacuum_analyze_threshold);'
            ),
        ),
        migrations.RunSQL(
            sql='ANALYZE api_facility;',
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]

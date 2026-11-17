# Keep api_facility planner statistics fresh enough for the
# is_candidate NOT EXISTS guard in FacilityIndexNewManager.without_candidates.
#
# is_candidate was added in 0237 with every row false, so the column
# statistics recorded "no candidates". Candidates (e.g. earth_genome
# satellite detections) are a small fraction of api_facility, so they never
# reached the default autovacuum_analyze_scale_factor (10% of the table) that
# triggers a re-analyze. The planner kept estimating 1 candidate row against
# ~16k real ones and chose a nested-loop anti join that compared every
# result row with every candidate: COUNT(*) for GET /api/facilities/
# ?countries=CN took ~180 s (1.8 billion join-filter comparisons) and
# CloudFront returned 504.
#
# 1. ANALYZE now, so the deploy itself fixes the estimate.
# 2. Re-analyze after 1% of rows change instead of 10%, so the estimate
#    keeps up as candidates are added.
#
# Both statements take only a SHARE UPDATE EXCLUSIVE lock, which does not
# block reads or writes.

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0283_list_cleaning_pipeline_meta'),
    ]

    operations = [
        migrations.RunSQL(
            sql=(
                'ALTER TABLE api_facility '
                'SET (autovacuum_analyze_scale_factor = 0.01);'
            ),
            reverse_sql=(
                'ALTER TABLE api_facility '
                'RESET (autovacuum_analyze_scale_factor);'
            ),
        ),
        migrations.RunSQL(
            sql='ANALYZE api_facility;',
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]

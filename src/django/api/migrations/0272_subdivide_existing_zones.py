from django.db import connection, migrations
from django.db.migrations import RunPython

from api.migrations._migration_helper import MigrationHelper

helper = MigrationHelper(connection)


def subdivide_existing_zones(apps, schema_editor):
    helper.run_sql_files(['0272_subdivide_zones.sql'])


def merge_pieces_back(apps, schema_editor):
    helper.run_sql_files(['0272_revert_subdivide_zones.sql'])


class Migration(migrations.Migration):
    """
    OSDEV-3744, data step. Re-cuts every zone saved before subdivision
    existed, in place, with the ST_Subdivide budget ZoneSet.replace_zones
    applied when this migration was written (64 vertices), so no set
    needs re-uploading. Every piece carries its feature's value,
    feature_index and created_at, so coverage and labels are unchanged
    for every point except one lying exactly on a feature edge that is
    not axis-aligned: ST_Subdivide adds a vertex where a cut line meets
    that edge, which can move the edge by a floating-point rounding.
    The parity run on the 2.5M-row production-derived dump found no
    such location, so FacilityIndex.zone_set_ids is not recomputed.

    Runs in a transaction of its own, after 0271 has committed the
    schema change, so the DELETE and INSERT take only row locks and the
    readers of api_zone (the facility indexing trigger, location pages,
    the zone_set_ids recompute) see the old rows until commit and the
    new rows after it, never a gap and never a wait. See 0271 for why
    the two steps are not one migration.

    The reverse merges each feature's pieces back into one row (see
    0272_revert_subdivide_zones.sql for the floating-point caveat);
    0271's reverse then restores the one-row-per-feature constraint.
    """

    dependencies = [
        ('api', '0271_subdivide_zones'),
    ]

    operations = [
        RunPython(subdivide_existing_zones, merge_pieces_back),
    ]

from django.db.migrations import Migration, RunPython
from django.db import connection

from api.migrations._migration_helper import MigrationHelper

helper = MigrationHelper(connection)


def update_indexing_function(apps, schema_editor):
    """
    Replace index_sector() so the searchable FacilityIndex.sector column
    stays aligned with the sectors shown on the location profile.

    The previous version aggregated the sectors of every MATCHED or
    CONFIRMED_MATCH list item a facility ever received. The profile, however,
    displays only one list item per contributor (see
    regroup_items_for_sector_field in api/serializers/facility/utils.py), so
    sectors from a contributor's older, superseded items stayed searchable
    even though they are no longer displayed. Filtering by such a sector
    (e.g. "Toys") returned facilities whose profiles do not show it. See
    OSDEV-992.

    The new version selects, per contributor, the single list item the
    profile displays - mirroring the display sort order exactly: items from
    active sources first, then by facility match activity (the display sorts
    matches flagged inactive first; mirrored bug-for-bug so search and
    display stay in lockstep), then by most recent updated_at. Claim sectors
    are likewise reduced to the latest approved claim per contributor.

    Known display-side limitation mirrored here: when the profile is
    requested with created_at_of_data_points=true it sorts by created_at
    instead of updated_at, which can select a different item per
    contributor. A single indexed column can only mirror one ordering; the
    default (updated_at) is used.
    """
    helper.run_sql_files([
        '0221_index_sector.sql'
    ])


def revert_indexing_function(apps, schema_editor):
    helper.run_sql_files([
        '0130_index_sector.sql'
    ])


class Migration(Migration):

    dependencies = [
        ('api', '0222_remove_closing_date_from_facility_claim'),
    ]

    operations = [
        RunPython(update_indexing_function, revert_indexing_function)
    ]

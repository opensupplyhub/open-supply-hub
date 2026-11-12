from django.db import connection, migrations, models

from api.migrations._migration_helper import MigrationHelper

helper = MigrationHelper(connection)

NEW_SQL_FILES = [
    '0272_index_contributors.sql',
    '0272_index_contributors_count.sql',
    '0272_index_facility_names.sql',
    '0272_index_facility_addresses.sql',
    '0272_index_facility_list_items.sql',
    '0272_index_extended_fields.sql',
    '0272_index_created_from_info.sql',
    '0272_index_item_sectors.sql',
    '0272_index_approved_claim.sql',
    '0272_index_claim_info.sql',
    '0272_index_claim_sectors.sql',
    '0272_organization_indexing_triggers.sql',
]

PREVIOUS_SQL_FILES = [
    '0225_index_contributors.sql',
    '0130_index_contributors_count.sql',
    '0225_index_facility_names.sql',
    '0225_index_facility_addresses.sql',
    '0225_index_facility_list_items.sql',
    '0225_index_extended_fields.sql',
    '0225_index_created_from_info.sql',
    '0225_index_item_sectors.sql',
    '0221_index_approved_claim.sql',
    '0221_index_claim_info.sql',
    '0130_index_claim_sectors.sql',
    '0272_revert_organization_indexing_triggers.sql',
    # Puts back the guard that 0271 added and this migration removes.
    '0271_skip_indexing_on_organization_stamp.sql',
]

# Production locations that already have a contribution or a claim
# recorded against an organization. Their index rows were written by the
# previous functions and still name the member's contributor.
REINDEX_ATTRIBUTED_FACILITIES = """
    DO $$
    DECLARE facility_ids TEXT[];
    BEGIN
        SELECT COALESCE(array_agg(DISTINCT attributed.facility_id), '{}')
        INTO facility_ids
        FROM (
            SELECT afli.facility_id
            FROM api_facilitylistitem afli
            JOIN api_source asrc ON asrc.id = afli.source_id
            WHERE asrc.organization_id IS NOT NULL
                AND afli.facility_id IS NOT NULL
            UNION
            SELECT afc.facility_id
            FROM api_facilityclaim afc
            WHERE afc.organization_id IS NOT NULL
        ) AS attributed;

        IF array_length(facility_ids, 1) > 0 THEN
            CALL index_facilities_by(facility_ids);
        END IF;
    END $$;
"""

NAME_HELP_TEXT = (
    'The name the organization is shown under: to its members, and '
    'publicly as the contributor of the production location data its '
    'members contribute.'
)


def reindex_attributed_facilities():
    with connection.cursor() as cursor:
        cursor.execute(REINDEX_ATTRIBUTED_FACILITIES)


def show_organization_name(apps, schema_editor):
    helper.run_sql_files(NEW_SQL_FILES)
    reindex_attributed_facilities()


def show_contributor_name(apps, schema_editor):
    helper.run_sql_files(PREVIOUS_SQL_FILES)
    reindex_attributed_facilities()


class Migration(migrations.Migration):
    """
    Shows the organization as the contributor of the data its members
    contribute.

    The facility index functions that build contributor attribution are
    re-created so that a contribution recorded against an organization
    (organization_id on its source or claim) carries the organization's
    name in place of the member's contributor name. The index therefore
    has to be refreshed when a contribution is attributed to an
    organization, so the guard added by 0271 is removed, and when an
    organization is renamed, so api_organization gets an indexing
    trigger. Production locations that are already attributed to an
    organization are re-indexed; on an installation where the
    organization level has not been used there are none.
    """

    dependencies = [
        ('api', '0271_skip_indexing_on_organization_stamp'),
    ]

    operations = [
        migrations.RunPython(show_organization_name, show_contributor_name),
        migrations.AlterField(
            model_name='organization',
            name='name',
            field=models.CharField(
                help_text=NAME_HELP_TEXT,
                max_length=200,
                unique=True,
            ),
        ),
        migrations.AlterField(
            model_name='historicalorganization',
            name='name',
            field=models.CharField(
                db_index=True,
                help_text=NAME_HELP_TEXT,
                max_length=200,
            ),
        ),
    ]

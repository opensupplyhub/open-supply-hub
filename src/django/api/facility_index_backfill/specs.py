"""SQL specs and registry for targeted FacilityIndex backfills."""

from typing import TypedDict

from django.core.management.base import CommandError

NON_EMPTY_CONTRIBUTORS_FILTER = (
    "cardinality(COALESCE(contributors, '{}')) > 0"
)

# Only facilities that already have an indexed claim need the claim_info
# refresh; index_claim_info() returns NULL for everything else, so this skips
# the millions of unclaimed rows.
CLAIMED_FACILITIES_FILTER = "claim_info IS NOT NULL"


class FacilityIndexFieldSpec(TypedDict, total=False):
    """Configuration for backfilling one logical field group."""

    columns: dict[str, str]
    filter_sql: str
    from_clause: str
    id_column: str


# Each entry defines one logical field group to backfill on FacilityIndex.
# Column expressions mirror index_facilities() in
# sqls/0171_index_facilities.sql.
#
# Keep this registry in sync when FacilityIndex changes:
# add or update field groups whenever a new indexed column is introduced or
# an index_*() function changes and a targeted post-deploy backfill is needed.
FACILITY_INDEX_FIELD_SPECS: dict[str, FacilityIndexFieldSpec] = {
    'contributors': {
        'columns': {
            'contributors': (
                "COALESCE("
                "(SELECT array_agg(contributor) "
                "FROM index_contributors(afi.id)), "
                "'{}'"
                ")"
            ),
        },
        'filter_sql': NON_EMPTY_CONTRIBUTORS_FILTER,
    },
    'claim_info': {
        'columns': {
            'claim_info': (
                "COALESCE("
                "(SELECT claim_info FROM index_claim_info(afi.id))"
                ")"
            ),
        },
        'filter_sql': CLAIMED_FACILITIES_FILTER,
    },
}


def list_field_names() -> list[str]:
    """Return registered backfill field group names in sorted order."""
    return sorted(FACILITY_INDEX_FIELD_SPECS.keys())


def get_field_spec(field_name: str) -> FacilityIndexFieldSpec:
    """Look up the backfill spec for a field group name."""
    try:
        return FACILITY_INDEX_FIELD_SPECS[field_name]
    except KeyError as exc:
        available = ', '.join(list_field_names())
        raise CommandError(
            f'Unknown field group "{field_name}". '
            f'Available groups: {available}.'
        ) from exc


def build_count_sql(spec: FacilityIndexFieldSpec) -> str:
    """Build SQL that counts rows assigned to one hash partition worker."""
    from_clause = spec.get('from_clause', 'FROM api_facilityindex afi')
    id_column = spec.get('id_column', 'afi.id')
    filter_sql = spec.get('filter_sql')
    filter_part = f'AND {filter_sql}' if filter_sql else ''
    partition_predicate = (
        f'mod(abs(hashtext({id_column}::text)::bigint), '
        f'%(workers)s) = %(worker_id)s'
    )

    return f"""
SELECT COUNT(*)
{from_clause}
WHERE {partition_predicate}
  {filter_part}
"""


def build_update_sql(spec: FacilityIndexFieldSpec) -> str:
    """Build batched UPDATE SQL for one hash partition worker."""
    set_parts = [
        f'{column} = {expression}'
        for column, expression in spec['columns'].items()
    ]
    set_parts.append('updated_at = now()')

    from_clause = spec.get('from_clause', 'FROM api_facilityindex afi')
    id_column = spec.get('id_column', 'afi.id')
    filter_sql = spec.get('filter_sql')
    filter_part = f'AND {filter_sql}' if filter_sql else ''
    partition_predicate = (
        f'mod(abs(hashtext({id_column}::text)::bigint), '
        f'%(workers)s) = %(worker_id)s'
    )

    return f"""
UPDATE api_facilityindex afi
SET
    {', '.join(set_parts)}
WHERE afi.id IN (
    SELECT {id_column}
    {from_clause}
    WHERE {id_column} > %(last_id)s
      AND {partition_predicate}
      {filter_part}
    ORDER BY {id_column}
    LIMIT %(batch_size)s
)
RETURNING afi.id
"""

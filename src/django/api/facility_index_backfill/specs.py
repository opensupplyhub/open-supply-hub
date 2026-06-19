from django.core.management.base import CommandError

NON_EMPTY_CONTRIBUTORS_FILTER = (
    "cardinality(COALESCE(contributors, '{}')) > 0"
)

# Each entry defines one logical field group to backfill on api_facilityindex.
# Column expressions mirror index_facilities() in
# sqls/0171_index_facilities.sql.
#
# Keep this registry in sync when FacilityIndex changes:
# add or update field groups whenever a new indexed column is introduced or
# an index_*() function changes and a targeted post-deploy backfill is needed.
FACILITY_INDEX_FIELD_SPECS = {
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
}


def list_field_names():
    return sorted(FACILITY_INDEX_FIELD_SPECS.keys())


def get_field_spec(field_name):
    try:
        return FACILITY_INDEX_FIELD_SPECS[field_name]
    except KeyError as exc:
        available = ', '.join(list_field_names())
        raise CommandError(
            f'Unknown field group "{field_name}". '
            f'Available groups: {available}.'
        ) from exc


def build_count_sql(spec):
    from_clause = spec.get('from_clause', 'FROM api_facilityindex afi')
    id_column = spec.get('id_column', 'afi.id')
    filter_sql = spec.get('filter_sql')
    filter_part = f'AND {filter_sql}' if filter_sql else ''

    return f"""
SELECT COUNT(*)
{from_clause}
WHERE mod(abs(hashtext({id_column}::text)), %(workers)s) = %(worker_id)s
  {filter_part}
"""


def build_update_sql(spec):
    set_parts = [
        f'{column} = {expression}'
        for column, expression in spec['columns'].items()
    ]
    set_parts.append('updated_at = now()')

    from_clause = spec.get('from_clause', 'FROM api_facilityindex afi')
    id_column = spec.get('id_column', 'afi.id')
    filter_sql = spec.get('filter_sql')
    filter_part = f'AND {filter_sql}' if filter_sql else ''

    return f"""
UPDATE api_facilityindex afi
SET
    {', '.join(set_parts)}
WHERE afi.id IN (
    SELECT {id_column}
    {from_clause}
    WHERE {id_column} > %(last_id)s
      AND mod(abs(hashtext({id_column}::text)), %(workers)s) = %(worker_id)s
      {filter_part}
    ORDER BY {id_column}
    LIMIT %(batch_size)s
)
RETURNING afi.id
"""

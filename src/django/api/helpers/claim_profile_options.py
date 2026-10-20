"""
Rewrite a claim-profile option's stored value across existing claims.

Affiliations and certifications are stored on `api_facilityclaim` as
plain string arrays: the option's name *is* the stored value. Renaming
an option (in the Django admin, or in a data migration) therefore has to
rewrite every claim holding the old name, or those claims would keep
showing, indexing and exporting it.

Kept free of model imports so data migrations can call it too.
"""

CLAIM_OPTION_COLUMNS = frozenset((
    'facility_affiliations',
    'facility_certifications',
))

CLAIM_TABLES = (
    'api_facilityclaim',
    # The history table is rewritten as well: a rename is a new label for
    # the same option, not a change the claimant made, so the claim's
    # change log should not suddenly show "Sustainable Apparel Coalition
    # -> Cascale" on its next edit.
    'api_historicalfacilityclaim',
)


def rename_claim_option_value(connection, column, old_value, new_value):
    """
    Replace `old_value` with `new_value` in `column` on every claim (and
    its history rows), then bump `updated_at` on the affected facilities.

    The facility bump is what makes the change reach OpenSearch: the
    Logstash production-locations sync selects rows by
    `api_facility.updated_at`, not by the claim's. The claim's own
    `updated_at` is deliberately left alone, because the sync reads it
    as the "claimed at" date.

    A claim that already holds `new_value` simply loses `old_value`, so
    the array never ends up with the same name twice.

    Args:
        connection: A Django database connection (or a migration's
            `schema_editor.connection`).
        column: `facility_affiliations` or `facility_certifications`.
        old_value: The option's previous name.
        new_value: The option's new name.

    Returns:
        The number of live (non-history) claims that were rewritten.
    """
    if column not in CLAIM_OPTION_COLUMNS:
        raise ValueError(f'Unsupported claim option column: {column}')
    if old_value == new_value:
        return 0

    # `column` is interpolated only after the allow-list check above;
    # the values always go through query parameters.
    update_sql = (
        f'UPDATE {{table}} SET {column} = CASE '
        f'WHEN %(new)s::varchar = ANY({column}) '
        f'THEN array_remove({column}, %(old)s::varchar) '
        f'ELSE array_replace({column}, %(old)s::varchar, %(new)s::varchar) '
        f'END '
        f'WHERE %(old)s::varchar = ANY({column}) '
        f'RETURNING facility_id'
    )
    params = {'old': old_value, 'new': new_value}

    facility_ids = set()
    live_claims_updated = 0
    with connection.cursor() as cursor:
        for table in CLAIM_TABLES:
            cursor.execute(update_sql.format(table=table), params)
            rows = cursor.fetchall()
            if table == 'api_facilityclaim':
                live_claims_updated = len(rows)
                facility_ids.update(row[0] for row in rows)

        if facility_ids:
            # clock_timestamp(), not now(): now() is frozen at the start of
            # the transaction, so in a long migration it could fall behind
            # a Logstash run that happened meanwhile, and the sync could
            # skip these rows.
            cursor.execute(
                'UPDATE api_facility SET updated_at = clock_timestamp() '
                'WHERE id = ANY(%s)',
                [sorted(facility_ids)],
            )

    return live_claims_updated

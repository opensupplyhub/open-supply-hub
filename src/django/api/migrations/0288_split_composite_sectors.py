from django.db import migrations


# Some rows store several sectors as one array element
# ("Apparel,Manufacturing,Textiles") instead of three. The sector filter
# matches elements exactly, so those locations are invisible to it. The
# ingest path has split on commas since 2024 (RowSectorSerializer's
# split_pattern), so this is residue: 3 list items from 2022, 13 from
# 2023, 458 from 2024, none since.
#
# A comma in a stored value does NOT prove it is a composite, so the
# split is conditional on every part already being a sector:
#
#   - "Professional, scientific and technical activities" is one
#     contributor-supplied phrase, not two sectors. Splitting it would
#     invent "Professional" and "scientific and technical activities".
#   - Values longer than the 50-character field limit were truncated
#     mid-word, leaving parts like "Manufactu" and "Label Manufac" that
#     no split can repair. The original text may survive in
#     api_facilitylistitem.raw_json; recovering it is not attempted here.
#
# Requiring every part to match api_sector.name leaves both classes
# untouched. See OSDEV-3923.
SPLIT_SQL = """
WITH rewritten AS (
    SELECT
        source.id,
        source.sector AS old_sector,
        ARRAY(
            SELECT DISTINCT btrim(part)
            FROM unnest(source.sector) AS element,
                 LATERAL unnest(
                     CASE
                         WHEN position(',' IN element) > 0
                              AND NOT EXISTS (
                                  SELECT 1
                                  FROM unnest(
                                      string_to_array(element, ',')
                                  ) AS candidate
                                  WHERE NOT EXISTS (
                                      SELECT 1 FROM api_sector s
                                      WHERE s.name = btrim(candidate)
                                  )
                              )
                         THEN string_to_array(element, ',')
                         ELSE ARRAY[element]
                     END
                 ) AS part
        )::varchar[] AS new_sector
    FROM {table} AS source
    WHERE EXISTS (
        SELECT 1 FROM unnest(source.sector) AS element
        WHERE position(',' IN element) > 0
    )
)
UPDATE {table} AS target
SET sector = rewritten.new_sector
FROM rewritten
WHERE target.id = rewritten.id
  AND rewritten.new_sector <> rewritten.old_sector;
"""

# A value that differs from a taxonomy sector only by case is invisible to
# the filter for the same reason: neither side lowercases. "packaging"
# against the taxonomy's "Packaging" is the only instance in production
# (6 rows), but the rewrite is general. See OSDEV-3923.
RECASE_SQL = """
UPDATE {table} AS target
SET sector = ARRAY(
    SELECT COALESCE(
        (
            SELECT s.name FROM api_sector s
            WHERE lower(s.name) = lower(element) AND s.name <> element
            LIMIT 1
        ),
        element
    )
    FROM unnest(target.sector) AS element
)::varchar[]
WHERE EXISTS (
    SELECT 1
    FROM unnest(target.sector) AS element
    JOIN api_sector s
      ON lower(s.name) = lower(element) AND s.name <> element
);
"""

# api_facilityindex is rebuilt from these tables by trigger on facility
# save, and the OpenSearch sync reads facility.updated_at, so both need
# the touch to notice the rewrite. As 0263 does.
TOUCH_FACILITIES_SQL = """
UPDATE api_facility f
SET updated_at = NOW()
WHERE EXISTS (
    SELECT 1 FROM api_facilitylistitem li
    WHERE li.facility_id = f.id AND li.id = ANY(%(list_item_ids)s)
)
OR EXISTS (
    SELECT 1 FROM api_facilityclaim c
    WHERE c.facility_id = f.id AND c.id = ANY(%(claim_ids)s)
);
"""

AFFECTED_SQL = """
SELECT id FROM {table}
WHERE EXISTS (
    SELECT 1 FROM unnest(sector) AS element
    WHERE position(',' IN element) > 0
       OR EXISTS (
           SELECT 1 FROM api_sector s
           WHERE lower(s.name) = lower(element) AND s.name <> element
       )
);
"""

TABLES = ('api_facilitylistitem', 'api_facilityclaim')


def split_composite_sectors(apps, schema_editor):
    connection = schema_editor.connection
    affected = {}
    with connection.cursor() as cursor:
        for table in TABLES:
            cursor.execute(AFFECTED_SQL.format(table=table))
            affected[table] = [row[0] for row in cursor.fetchall()]

        for table in TABLES:
            cursor.execute(SPLIT_SQL.format(table=table))
            cursor.execute(RECASE_SQL.format(table=table))

        cursor.execute(
            TOUCH_FACILITIES_SQL,
            {
                'list_item_ids': affected['api_facilitylistitem'],
                'claim_ids': affected['api_facilityclaim'],
            },
        )


class Migration(migrations.Migration):
    """
    Split stored multi-sector values that were never split, and rewrite
    sector values that differ from the taxonomy only by case, so the
    affected production locations become visible to the sector filter.

    Not reversible: once split, those rows are indistinguishable from
    rows that were always correct, and re-joining them would corrupt
    locations that legitimately carry several sectors.

    See OSDEV-3923.
    """

    dependencies = [
        ('api', '0284_zone_set_last_upload_sha256'),
    ]

    operations = [
        migrations.RunPython(
            split_composite_sectors,
            migrations.RunPython.noop,
        ),
    ]

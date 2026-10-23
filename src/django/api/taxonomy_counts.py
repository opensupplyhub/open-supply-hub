from django.db import connection

from api.isic_taxonomy import revisions

# Locations per search entry, in one pass over api_facilityindex. Each
# location's codes are joined to the entries they count toward (its own, and
# through the UN correspondence the other revision's), so a location counts
# once per entry whichever revision it was uploaded under. Every location
# with an ISIC code has a section (parent levels are stored), so the WHERE
# skips the rest. Candidates are excluded as in
# FacilityIndex.objects.without_candidates(), which the search starts from.
COUNTS_SQL = """
    WITH located AS (
        SELECT fi.id, '4' AS revision, code
        FROM api_facilityindex fi,
            unnest(
                fi.isic_section || fi.isic_division
                || fi.isic_group || fi.isic_class
            ) AS code
        WHERE cardinality(fi.isic_section) > 0
        UNION ALL
        SELECT fi.id, '5' AS revision, code
        FROM api_facilityindex fi,
            unnest(
                fi.isic5_section || fi.isic5_division
                || fi.isic5_group || fi.isic5_class
            ) AS code
        WHERE cardinality(fi.isic5_section) > 0
    )
    -- Distinct (location, entry) pairs first: about twice as fast as
    -- count(DISTINCT) per entry.
    SELECT entry_id, count(*)
    FROM (
        SELECT DISTINCT located.id, entry.entry_id
        FROM located
        JOIN unnest(
            %(revisions)s::text[], %(codes)s::text[], %(ids)s::text[]
        ) AS entry(revision, code, entry_id)
            ON entry.revision = located.revision
            AND entry.code = located.code
        WHERE NOT EXISTS (
            SELECT 1 FROM api_facility af
            WHERE af.id = located.id AND af.is_candidate
        )
    ) AS pairs
    GROUP BY entry_id
"""


def compute_isic_counts():
    '''Location counts keyed by search entry id, e.g. {"4:1410": 12}.'''
    revision_list, codes, ids = zip(*revisions.count_map())
    with connection.cursor() as cursor:
        cursor.execute(COUNTS_SQL, {
            'revisions': list(revision_list),
            'codes': list(codes),
            'ids': list(ids),
        })
        return dict(cursor.fetchall())

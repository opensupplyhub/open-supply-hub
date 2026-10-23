from django.db import connection

from api.models.facility.facility_index import FacilityIndex
from api.models.facility.facility_manager_index_new import build_isic_filter

# Locations per ISIC node, in one pass over api_facilityindex. Every location
# with an ISIC code has a section (ancestors are derived), so the WHERE skips
# the rest. With include_mapped, a location counts once under a node whether
# its code was submitted, mapped, or both (DISTINCT per row). Candidates are
# excluded as in FacilityIndex.objects.without_candidates(), which the
# search starts from.
COUNTS_SQL = """
    SELECT nodes.level, code.value, count(*)
    FROM api_facilityindex fi
    CROSS JOIN LATERAL (VALUES
        ('section', fi.isic_section
            || CASE WHEN %(mapped)s THEN fi.isic_mapped_section END),
        ('division', fi.isic_division
            || CASE WHEN %(mapped)s THEN fi.isic_mapped_division END),
        ('group', fi.isic_group
            || CASE WHEN %(mapped)s THEN fi.isic_mapped_group END),
        ('class', fi.isic_class
            || CASE WHEN %(mapped)s THEN fi.isic_mapped_class END)
    ) AS nodes(level, codes)
    CROSS JOIN LATERAL (SELECT DISTINCT unnest(nodes.codes)) AS code(value)
    WHERE (
        cardinality(fi.isic_section) > 0
        OR (%(mapped)s AND cardinality(fi.isic_mapped_section) > 0)
      )
      AND NOT EXISTS (
        SELECT 1 FROM api_facility af
        WHERE af.id = fi.id AND af.is_candidate
      )
    GROUP BY nodes.level, code.value
"""


def compute_isic4_counts(include_mapped=False):
    '''Location counts keyed by level:code, e.g. {"class:1410": 12}.'''
    with connection.cursor() as cursor:
        cursor.execute(COUNTS_SQL, {'mapped': include_mapped})
        return {
            f'{level}:{code}': count
            for level, code, count in cursor.fetchall()
            if code
        }


def compute_isic4_mapped_extra_count(parsed_isic_filters):
    '''
    How many more locations the selected ISIC nodes match when mapped values
    are included: the number behind the "(+N)" next to the opt-in.
    '''
    if not parsed_isic_filters:
        return 0

    return (
        FacilityIndex.objects.without_candidates()
        .filter(build_isic_filter(parsed_isic_filters, include_mapped=True))
        .exclude(build_isic_filter(parsed_isic_filters))
        .count()
    )

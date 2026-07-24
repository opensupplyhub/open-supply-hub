from datetime import date
from typing import Dict, List

from django.db import connection

from api.constants import FacilityClaimStatuses
from api.models.extended_field import ExtendedField
from api.services.change_intelligence_name_normalization import name_changed

# Change Intelligence Phase 1 report columns, in the agreed output order.
# DUNS/LEI/GLN/Tier/Confidence Level are placeholders pending the GODIN/LEI
# mapping work (OSDEV-2676) and DQS/Confidence scope (OSDEV-2845) -- always
# empty here, per the signed-off product decision in the OSDEV-2994 exercise.
REPORT_COLUMNS = [
    'OS ID', 'Facility Name', 'DUNS', 'LEI', 'GLN', 'Country', 'Tier',
    'Change Type', 'Field Changed', 'Previous Value', 'New Value',
    'Date Detected', 'Data Source', 'Confidence Level', 'Claimed Status',
    'Suggested Next Action',
]

SUGGESTED_NEXT_ACTION = {
    'Claimed status': 'Review claim / verify operator',
    'Name / address': 'Confirm identity still matches your record',
    'Material facility': 'Re-assess sourcing relevance',
}

# Read-only over django-simple-history's historical_* tables (RFC Sec 3.1 /
# OSDEV-2844) -- no schema changes. Each signal branch diffs a field against
# its own immediately-preceding historical value via LAG(). The name/address
# branches share one CTE (fac_hist) since they read the same history table.
#
# The 'name' branch only emits raw-string-diff *candidates* here; a Python
# post-filter (name_changed()) drops formatting/legal-suffix-only diffs that
# aren't a material rename -- that normalization can't be expressed in SQL.
_REPORT_SQL = """
WITH scope AS (
    SELECT unnest(%(watchlist)s::text[]) AS facility_id
),
claim_hist AS (
    SELECT
        facility_id AS os_id,
        history_date,
        status,
        LAG(status) OVER (PARTITION BY id ORDER BY history_date)
            AS prev_status
    FROM api_historicalfacilityclaim
    WHERE facility_id IN (SELECT facility_id FROM scope)
),
sig_claim AS (
    SELECT
        os_id, history_date AS date_detected,
        'Claimed status' AS change_type, 'claim status' AS field_changed,
        prev_status AS previous_value, status AS new_value,
        'OS Hub -- Claim' AS data_source
    FROM claim_hist
    WHERE prev_status IS NOT NULL
      AND status IS DISTINCT FROM prev_status
      AND history_date BETWEEN %(start_date)s AND %(end_date)s
),
ef_hist AS (
    SELECT
        facility_id AS os_id,
        history_date,
        value ->> 'raw_values' AS raw_values,
        LAG(value ->> 'raw_values')
            OVER (PARTITION BY id ORDER BY history_date) AS prev_raw_values
    FROM api_historicalextendedfield
    WHERE field_name = %(facility_type_field_name)s
      AND facility_id IN (SELECT facility_id FROM scope)
),
sig_material AS (
    SELECT
        os_id, history_date AS date_detected,
        'Material facility' AS change_type, 'facility_type' AS field_changed,
        left(prev_raw_values, 120) AS previous_value,
        left(raw_values, 120) AS new_value,
        'OS Hub -- Extended field' AS data_source
    FROM ef_hist
    WHERE prev_raw_values IS NOT NULL
      AND raw_values IS DISTINCT FROM prev_raw_values
      AND history_date BETWEEN %(start_date)s AND %(end_date)s
),
fac_hist AS (
    SELECT
        id AS os_id, history_date, name, address, country_code,
        LAG(name) OVER w AS prev_name,
        LAG(address) OVER w AS prev_address,
        LAG(country_code) OVER w AS prev_country_code
    FROM api_historicalfacility
    WHERE id IN (SELECT facility_id FROM scope)
    WINDOW w AS (PARTITION BY id ORDER BY history_date)
),
sig_address AS (
    SELECT
        os_id, history_date AS date_detected,
        'Name / address' AS change_type, 'address' AS field_changed,
        prev_address AS previous_value, address AS new_value,
        'OS Hub -- Facility' AS data_source
    FROM fac_hist
    WHERE prev_address IS NOT NULL
      AND address IS DISTINCT FROM prev_address
      AND history_date BETWEEN %(start_date)s AND %(end_date)s
),
sig_country AS (
    SELECT
        os_id, history_date AS date_detected,
        'Name / address' AS change_type, 'country_code' AS field_changed,
        prev_country_code AS previous_value, country_code AS new_value,
        'OS Hub -- Facility' AS data_source
    FROM fac_hist
    WHERE prev_country_code IS NOT NULL
      AND country_code IS DISTINCT FROM prev_country_code
      AND history_date BETWEEN %(start_date)s AND %(end_date)s
),
sig_name_candidates AS (
    SELECT
        os_id, history_date AS date_detected,
        'Name / address' AS change_type, 'name' AS field_changed,
        prev_name AS previous_value, name AS new_value,
        'OS Hub -- Facility' AS data_source
    FROM fac_hist
    WHERE prev_name IS NOT NULL
      AND name IS DISTINCT FROM prev_name
      AND history_date BETWEEN %(start_date)s AND %(end_date)s
)
SELECT * FROM sig_claim
UNION ALL SELECT * FROM sig_material
UNION ALL SELECT * FROM sig_address
UNION ALL SELECT * FROM sig_country
UNION ALL SELECT * FROM sig_name_candidates
"""


def _fetch_change_candidates(
    os_ids: List[str], start_date: date, end_date: date,
) -> List[Dict]:
    params = {
        'watchlist': list(os_ids),
        'start_date': start_date,
        'end_date': end_date,
        'facility_type_field_name': ExtendedField.FACILITY_TYPE,
    }
    with connection.cursor() as cursor:
        cursor.execute(_REPORT_SQL, params)
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def _claimed_facility_ids(os_ids: List[str]) -> set:
    from api.models.facility.facility_claim import FacilityClaim

    return set(
        FacilityClaim.objects
        .filter(facility_id__in=os_ids, status=FacilityClaimStatuses.APPROVED)
        .values_list('facility_id', flat=True)
    )


def _facility_names_and_countries(os_ids: List[str]) -> Dict[str, Dict]:
    from api.models.facility.facility import Facility

    return {
        f['id']: f
        for f in Facility.objects.filter(id__in=os_ids)
        .values('id', 'name', 'country_code')
    }


def get_change_intelligence_report(
    os_ids: List[str], start_date: date, end_date: date,
) -> List[Dict]:
    """Watchlist-scoped Change Intelligence report: one row per meaningful
    change across the 3 native signals (claimed status, name/address,
    material facility type), for facilities in `os_ids` with a change
    detected in `history_date` between `start_date` and `end_date`
    (inclusive). Read-only; no schema changes."""
    if not os_ids:
        return []

    candidates = _fetch_change_candidates(os_ids, start_date, end_date)
    claimed_ids = _claimed_facility_ids(os_ids)
    facilities = _facility_names_and_countries(os_ids)

    rows = []
    for c in candidates:
        if c['field_changed'] == 'name' and not name_changed(
            c['previous_value'], c['new_value']
        ):
            continue

        facility = facilities.get(c['os_id'], {})
        rows.append({
            'OS ID': c['os_id'],
            'Facility Name': facility.get('name', ''),
            'DUNS': '',
            'LEI': '',
            'GLN': '',
            'Country': facility.get('country_code', ''),
            'Tier': '',
            'Change Type': c['change_type'],
            'Field Changed': c['field_changed'],
            'Previous Value': c['previous_value'],
            'New Value': c['new_value'],
            'Date Detected': c['date_detected'],
            'Data Source': c['data_source'],
            'Confidence Level': '',
            'Claimed Status': (
                'Claimed' if c['os_id'] in claimed_ids else 'Unclaimed'
            ),
            'Suggested Next Action': SUGGESTED_NEXT_ACTION[c['change_type']],
        })

    rows.sort(key=lambda r: (r['Date Detected'], r['OS ID']), reverse=True)
    return rows

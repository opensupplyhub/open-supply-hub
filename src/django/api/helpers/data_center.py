"""Helpers for classifying a facility as a data center (OSDEV-3067).

A facility is classified as a data center via its ``facility_type``
``ExtendedField`` value(s) - there is no dedicated column. This module is the
single source of truth for the "is this a data center?" question; guards
(merge / link), downloads, grouping, and any other caller should use
``is_data_center`` rather than re-implementing the check inline.
"""
import logging

from api.facility_type_processing_type import ALL_FACILITY_TYPES, DATA_CENTER

log = logging.getLogger(__name__)

# The human-readable facility_type value stored in matched_values, e.g.
# "Data Center". Sourced from the taxonomy so there is one definition.
DATA_CENTER_FACILITY_TYPE = ALL_FACILITY_TYPES[DATA_CENTER]

# Index of the facility_type within a matched_values entry
# (field_type, match_type, facility_type, processing_type).
FACILITY_TYPE_INDEX = 2


def matched_values_include_data_center(value):
    """
    Return True if a single facility_type ExtendedField ``value`` resolves to
    the Data Center facility type.

    ``value`` has the shape
    ``{"raw_values": ..., "matched_values": [[field_type, match_type,
    facility_type, processing_type], ...]}``.
    """
    if not isinstance(value, dict):
        return False

    for matched in value.get('matched_values') or []:
        if (
            isinstance(matched, (list, tuple))
            and len(matched) > FACILITY_TYPE_INDEX
            and matched[FACILITY_TYPE_INDEX] == DATA_CENTER_FACILITY_TYPE
        ):
            return True

    return False


def is_data_center(facility):
    """
    Return True if ``facility`` is classified as a data center.

    Derived from the facility's ``facility_type`` ExtendedField(s); no
    dedicated column is used. ``facility`` may be a ``Facility`` instance or an
    OS ID.

    A facility is treated as a data center if **any** of its ``facility_type``
    values resolves to "Data Center". NOTE (OSDEV-3067 AC#3): the tie-break for
    a facility carrying both "Data Center" and a production facility_type is an
    open team decision; this "any" rule is the interim default and is the safe
    choice for the merge/link guards (a mixed record is treated as a data
    center, so it cannot be merged into a pure production location).
    """
    # Imported lazily to avoid importing models at app-load time.
    from api.models.extended_field import ExtendedField

    if facility is None:
        return False

    values = ExtendedField.objects.filter(
        facility=facility,
        field_name=ExtendedField.FACILITY_TYPE,
    ).values_list('value', flat=True)

    return any(matched_values_include_data_center(v) for v in values)


# --- Per-row provenance capture for FacilityListItem ---
# These names match the incoming contribution column names. Values are
# read from the raw row (not the cleaned fields) so URLs, dates, and
# free text are preserved unmodified.
PROVENANCE_FIELDS = (
    'source_name',
    'source_link',
    'information_source_type',
    'date_of_source',
    'notes',
    'data_collection_methodology',
    'ai_usage_notes',
)


DATE_OF_SOURCE_FORMAT_MESSAGE = (
    'must be a date in YYYY, YYYY-MM, or YYYY-MM-DD format'
)

# Mirrors the FacilityListItem column sizes. The remaining provenance fields
# are TextFields and therefore unbounded.
PROVENANCE_MAX_LENGTHS = {
    'source_name': 500,
    'source_link': 2000,
    'information_source_type': 200,
}


def _clean_provenance_text(value, max_length=None):
    """
    Return a trimmed string when the value is usable, otherwise None.

    Non-string values are rejected rather than coerced, and values longer
    than the column can hold are rejected so they cannot fail at the database
    layer.
    """
    if not isinstance(value, str):
        return None

    cleaned = value.strip()
    if not cleaned:
        return None
    if max_length is not None and len(cleaned) > max_length:
        return None

    return cleaned


def _clean_provenance_url(value):
    """
    Return a valid http(s) URL, or None.

    The link is rendered as a clickable anchor, so schemes are restricted to
    http and https - a value such as a `javascript:` URI must never be stored
    and offered as a link.
    """
    from django.core.exceptions import ValidationError
    from django.core.validators import URLValidator

    cleaned = _clean_provenance_text(
        value, PROVENANCE_MAX_LENGTHS['source_link']
    )
    if cleaned is None:
        return None

    try:
        URLValidator(schemes=['http', 'https'])(cleaned)
    except ValidationError:
        return None

    return cleaned


def normalize_date_of_source(value):
    """
    Validate and normalize a date_of_source value as an ISO 8601
    reduced-precision date string: YYYY, YYYY-MM, or YYYY-MM-DD — whatever
    precision the external source provides. Returns the normalized string,
    or None when the value is not a valid (partial) date.
    """
    from datetime import date

    if isinstance(value, date):
        return value.isoformat()
    if not isinstance(value, str):
        return None

    normalized = value.strip()
    parts = normalized.split('-')

    if not all(part.isdigit() for part in parts):
        return None

    if len(parts) == 1 and len(parts[0]) == 4:
        return normalized
    if len(parts) == 2 and len(parts[0]) == 4 and len(parts[1]) == 2:
        if 1 <= int(parts[1]) <= 12:
            return normalized
        return None
    if (
        len(parts) == 3
        and len(parts[0]) == 4
        and len(parts[1]) == 2
        and len(parts[2]) == 2
    ):
        try:
            date(int(parts[0]), int(parts[1]), int(parts[2]))
        except ValueError:
            return None
        return normalized

    return None


def extract_provenance(raw_data):
    """
    Return a dict of provenance field -> value from a raw contribution row,
    validated so the values can always be persisted.

    Every value is checked centrally here because this is the single entry
    point used by all FacilityListItem creation paths (list upload, legacy
    API and SLC approval), and only the v1 API validates provenance up front:

    * values must be strings; other types are rejected rather than coerced;
    * values are trimmed, and rejected when longer than the column allows, so
      they cannot fail at the database layer;
    * `source_link` must be a valid http(s) URL, since it is rendered as a
      clickable link;
    * `date_of_source` must be an ISO reduced-precision date (YYYY, YYYY-MM
      or YYYY-MM-DD).

    Invalid values are logged and omitted rather than failing the row: this
    is supplementary metadata, and dropping the whole contribution because a
    source link is malformed would lose the location data too. Absent or
    rejected values leave the FacilityListItem columns as NULL.
    """
    if not raw_data:
        return {}

    provenance = {}
    for field in PROVENANCE_FIELDS:
        raw_value = raw_data.get(field)
        if raw_value in (None, ''):
            continue

        if field == 'date_of_source':
            value = normalize_date_of_source(raw_value)
        elif field == 'source_link':
            value = _clean_provenance_url(raw_value)
        else:
            value = _clean_provenance_text(
                raw_value, PROVENANCE_MAX_LENGTHS.get(field)
            )

        if value is None:
            log.warning(
                'Ignoring invalid provenance value for field "%s".', field
            )
            continue

        provenance[field] = value

    return provenance

"""Helpers for classifying a facility as a data center (OSDEV-3067).

A facility is classified as a data center via its ``facility_type``
``ExtendedField`` value(s) - there is no dedicated column. This module is the
single source of truth for the "is this a data center?" question; guards
(merge / link), downloads, grouping, and any other caller should use
``is_data_center`` rather than re-implementing the check inline.
"""
from api.facility_type_processing_type import ALL_FACILITY_TYPES, DATA_CENTER

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

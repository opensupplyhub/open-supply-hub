"""
Filtering an embedded map by the values of a contributor's own columns.

A contributor marks a visible embed field as filterable on the Embed settings
screen. Their embedded map then offers a dropdown for it, and sends the choice
as `embed_filters=<column>::<value>` (repeatable; every filter must match).

The values are read from `FacilityListItem.raw_json`, the contributor's
uploaded row keyed by column name, so nothing new has to be indexed. A cell can
hold several values separated by `|`, `;` or `,`; a filter matches the cell
when it equals any one of them, ignoring case.
"""
import re

from django.db.models.fields.json import KeyTextTransform

EMBED_FILTERS_PARAM = 'embed_filters'
SEPARATOR = '::'
VALUE_SPLIT_PATTERN = re.compile(r'[|;,]')
MAX_OPTIONS_PER_FIELD = 200


def _embed_contributor_id(params):
    contributor = params.get('contributor', None)
    if contributor is None:
        contributors = params.getlist('contributors')
        contributor = contributors[0] if contributors else None
    try:
        return int(contributor)
    except (TypeError, ValueError):
        return None


def _filterable_columns(contributor_id):
    from api.models.embed_field import EmbedField

    return set(
        EmbedField.objects.filter(
            embed_config__contributor__id=contributor_id,
            visible=True,
            filterable=True,
        ).values_list('column_name', flat=True)
    )


def _contributor_items(contributor_id):
    from api.models.facility.facility_list_item import FacilityListItem

    return FacilityListItem.objects.filter(
        source__contributor_id=contributor_id,
        source__is_active=True,
        facility__isnull=False,
    )


def parse_embed_filters(params):
    """Return the (column, value) pairs requested, skipping malformed ones."""
    pairs = []
    for raw in params.getlist(EMBED_FILTERS_PARAM):
        column, separator, value = raw.partition(SEPARATOR)
        column, value = column.strip(), value.strip()
        if separator and column and value:
            pairs.append((column, value))
    return pairs


def _value_pattern(value):
    """A regex matching a cell that holds `value` as one of its values."""
    return r'(^|[|;,])\s*' + re.escape(value) + r'\s*($|[|;,])'


def embed_filter_facility_id_sets(params):
    """
    Return one queryset of facility ids per requested embed filter; a
    facility has to be in all of them. Returns an empty list when the request
    is not an embedded map request or asks for no embed filters.

    A filter on a column the contributor has not made filterable matches
    nothing, so a hidden column cannot be probed through the filter.
    """
    if params.get('embed') != '1':
        return []
    pairs = parse_embed_filters(params)
    if not pairs:
        return []

    contributor_id = _embed_contributor_id(params)
    items = _contributor_items(contributor_id)
    if contributor_id is None:
        return [items.none().values('facility_id')]

    allowed = _filterable_columns(contributor_id)
    id_sets = []
    for column, value in pairs:
        if column not in allowed:
            return [items.none().values('facility_id')]
        id_sets.append(
            items.annotate(embed_value=KeyTextTransform(column, 'raw_json'))
            .filter(embed_value__iregex=_value_pattern(value))
            .values('facility_id')
        )
    return id_sets


def apply_embed_filters(facilities_qs, params):
    """Narrow a Facility or FacilityIndex queryset by the embed filters."""
    for facility_ids in embed_filter_facility_id_sets(params):
        facilities_qs = facilities_qs.filter(id__in=facility_ids)
    return facilities_qs


def split_values(cell):
    return [
        value.strip()
        for value in VALUE_SPLIT_PATTERN.split(str(cell))
        if value.strip()
    ]


def embed_filter_options(contributor):
    """
    The dropdown options for each of a contributor's filterable fields:
    `{column: [{'value': ..., 'count': <facilities>}, ...]}`, most common
    value first.
    """
    options = {}
    items = _contributor_items(contributor.id)
    for column in sorted(_filterable_columns(contributor.id)):
        facilities_by_value = {}
        rows = (
            items.annotate(embed_value=KeyTextTransform(column, 'raw_json'))
            .exclude(embed_value__isnull=True)
            .exclude(embed_value='')
            .values_list('facility_id', 'embed_value')
            .distinct()
        )
        for facility_id, cell in rows:
            for value in split_values(cell):
                facilities_by_value.setdefault(value, set()).add(facility_id)
        ranked = sorted(
            facilities_by_value.items(),
            key=lambda item: (-len(item[1]), item[0].lower()),
        )
        options[column] = [
            {'value': value, 'count': len(facility_ids)}
            for value, facility_ids in ranked[:MAX_OPTIONS_PER_FIELD]
        ]
    return options

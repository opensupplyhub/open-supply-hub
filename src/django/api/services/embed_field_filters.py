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

from django.db.models import (
    Case,
    Exists,
    F,
    FloatField,
    OuterRef,
    Q,
    Subquery,
    When,
)
from django.db.models.fields.json import KeyTextTransform
from django.db.models.functions import Cast, Lower, Trim

EMBED_FILTERS_PARAM = 'embed_filters'
COLOR_BY_PARAM = 'color_by'
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
    # Imported here: the Spotlight service reaches models that import this
    # module while they load.
    from api.services.embed_spotlight import apply_embed_spotlight_filter

    facilities_qs = apply_embed_spotlight_filter(facilities_qs, params)
    return facilities_qs


def split_values(cell):
    return [
        value.strip()
        for value in VALUE_SPLIT_PATTERN.split(str(cell))
        if value.strip()
    ]


def field_value_options(contributor_id, column):
    """
    The values a contributor's facilities have in `column`, with how many
    facilities have each, most common first.
    """
    facilities_by_value = {}
    rows = (
        _contributor_items(contributor_id)
        .annotate(embed_value=KeyTextTransform(column, 'raw_json'))
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
    return [
        {'value': value, 'count': len(facility_ids)}
        for value, facility_ids in ranked[:MAX_OPTIONS_PER_FIELD]
    ]


def embed_filter_options(contributor):
    """
    The dropdown options for each of a contributor's filterable fields:
    `{column: [{'value': ..., 'count': <facilities>}, ...]}`, most common
    value first.
    """
    return {
        column: field_value_options(contributor.id, column)
        for column in sorted(_filterable_columns(contributor.id))
    }


def embed_color_by_column(params):
    """
    The column whose value an embedded map's tiles should carry on each
    marker, so the map can color markers by it. Only the column the
    contributor chose as their `color_by_field` is ever sent; anything else
    asked for through `color_by` is ignored.
    """
    from api.models.embed_config import EmbedConfig

    if params.get('embed') != '1':
        return None
    column = params.get(COLOR_BY_PARAM)
    contributor_id = _embed_contributor_id(params)
    if not column or contributor_id is None:
        return None
    is_chosen = EmbedConfig.objects.filter(
        contributor__id=contributor_id, color_by_field=column
    ).exists()
    return column if is_chosen else None


def embed_color_value_subquery(params, column):
    """A facility's value in `column`, from the embed's contributor."""
    return Subquery(
        _contributor_items(_embed_contributor_id(params))
        .filter(facility=OuterRef('pk'))
        .annotate(embed_value=KeyTextTransform(column, 'raw_json'))
        .exclude(embed_value__isnull=True)
        .exclude(embed_value='')
        .order_by('-id')
        .values('embed_value')[:1]
    )


# --------------------------------------------------------------------------
# List order
# --------------------------------------------------------------------------
# An embedded map asks for its list with `sort_by=embed_default`; the
# contributor's saved choice decides what that means.
EMBED_DEFAULT_SORT = 'embed_default'
FIELD_SORT_PREFIX = 'field:'
NUMBER_PATTERN = r'^\s*[0-9]+(\.[0-9]+)?\s*$'


def resolve_embed_sort(params, sort_by):
    """Replace `embed_default` with the contributor's chosen list order."""
    from api.models.embed_config import EmbedConfig

    if sort_by != EMBED_DEFAULT_SORT:
        return sort_by
    contributor_id = _embed_contributor_id(params)
    chosen = None
    if params.get('embed') == '1' and contributor_id is not None:
        chosen = (
            EmbedConfig.objects.filter(contributor__id=contributor_id)
            .values_list('default_sort', flat=True)
            .first()
        )
    return chosen or 'name_asc'


def embed_field_sort(params, sort_by):
    """
    Return `(column, descending)` when `sort_by` asks to order an embedded
    map's list by one of the contributor's visible fields, else None.
    """
    from api.models.embed_field import EmbedField

    if not sort_by or params.get('embed') != '1':
        return None
    descending = sort_by.startswith('-')
    key = sort_by[1:] if descending else sort_by
    if not key.startswith(FIELD_SORT_PREFIX):
        return None
    column = key[len(FIELD_SORT_PREFIX):]
    contributor_id = _embed_contributor_id(params)
    if not column or contributor_id is None:
        return None
    is_visible = EmbedField.objects.filter(
        embed_config__contributor__id=contributor_id,
        column_name=column,
        visible=True,
    ).exists()
    return (column, descending) if is_visible else None


def order_by_embed_field(queryset, params, column, descending):
    """
    Order facilities by their value in one of the contributor's columns.
    Values that are plain numbers sort as numbers, ahead of text; facilities
    with no value come last either way. Name breaks ties.
    """
    queryset = queryset.annotate(
        embed_sort_value=embed_color_value_subquery(params, column),
    ).annotate(
        embed_sort_number=Case(
            When(
                embed_sort_value__regex=NUMBER_PATTERN,
                then=Cast(Trim(F('embed_sort_value')), FloatField()),
            ),
            default=None,
            output_field=FloatField(),
        ),
    )
    number = F('embed_sort_number')
    value = Lower(F('embed_sort_value'))
    if descending:
        ordering = [number.desc(nulls_last=True), value.desc(nulls_last=True)]
    else:
        ordering = [number.asc(nulls_last=True), value.asc(nulls_last=True)]
    return queryset, ordering


def embed_has_blurb(params):
    """
    For an embedded map whose contributor lists blurbed facilities first:
    an expression that is true for a facility with text in any of the
    contributor's visible blurb fields. None when that does not apply.
    """
    from api.models.embed_config import EmbedConfig
    from api.models.embed_field import EmbedField

    contributor_id = _embed_contributor_id(params)
    if params.get('embed') != '1' or contributor_id is None:
        return None
    if not EmbedConfig.objects.filter(
        contributor__id=contributor_id, blurbs_first=True
    ).exists():
        return None
    columns = list(
        EmbedField.objects.filter(
            embed_config__contributor__id=contributor_id,
            visible=True,
            display_as=EmbedField.BLURB,
        ).values_list('column_name', flat=True)
    )
    if not columns:
        return None

    items = _contributor_items(contributor_id).filter(
        facility=OuterRef('pk')
    )
    has_text = Q()
    for position, column in enumerate(columns):
        alias = 'embed_blurb_{}'.format(position)
        # Trimmed, so a cell holding only spaces does not count as a blurb.
        items = items.annotate(
            **{alias: Trim(KeyTextTransform(column, 'raw_json'))}
        )
        has_text |= Q(**{alias + '__isnull': False}) & ~Q(**{alias: ''})
    return Exists(items.filter(has_text))


def embed_settings_version(params):
    """
    A token that changes whenever an embedded map's contributor saves their
    embed settings, and is empty for any other request.

    The facility list for an embedded map depends on those settings (the
    list order, blurbs first, which fields each facility carries), so a
    cached list has to stop being served once they change.
    """
    from api.models.embed_config import EmbedConfig

    contributor_id = _embed_contributor_id(params)
    if params.get('embed') != '1' or contributor_id is None:
        return ''
    updated_at = (
        EmbedConfig.objects.filter(contributor__id=contributor_id)
        .values_list('updated_at', flat=True)
        .first()
    )
    return updated_at.isoformat() if updated_at else ''

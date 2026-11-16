"""
Spotlight on an embedded map: data about a contributor's facilities from
OS Hub's data partners.

A contributor with the Embed Deluxe package can choose to show it on their
map, for the partner field groups they pick. Their map can then ring the
facilities that have it, mark them in the list, show the data on a
facility's details, and offer it as a filter, sent as
`embed_spotlight=any` or `embed_spotlight=<group uuid>`.

Nothing here is shown unless the contributor has turned it on: an embedded
map otherwise only ever carries its own contributor's data.
"""
from django.db.models import Exists, OuterRef

from api.models.facility.partner_contributor_filter import (
    apply_partner_fields_or_filter,
)

EMBED_SPOTLIGHT_PARAM = 'embed_spotlight'
ANY_SPOTLIGHT = 'any'
DELUXE_EMBED_LEVEL = 3
MAX_SPOTLIGHT_GROUPS = 100


def available_spotlight_groups():
    """
    The partner field groups that have data to show: each with its active
    partner fields and the partners that contribute them, in display order.
    """
    from api.models.partner_field import PartnerField

    groups = {}
    fields = (
        PartnerField.objects.filter(active=True, group__isnull=False)
        .select_related('group')
        .prefetch_related('contributor_set')
        .order_by('group__order', 'group__name', 'name')
    )
    for field in fields:
        group = groups.setdefault(
            str(field.group.uuid),
            {
                'uuid': str(field.group.uuid),
                'name': field.group.name,
                'field_names': [],
                'contributor_ids': set(),
            },
        )
        group['field_names'].append(field.name)
        group['contributor_ids'].update(
            contributor.id for contributor in field.contributor_set.all()
        )
    return list(groups.values())


def _embed_contributor_id(params):
    contributor = params.get('contributor', None)
    if contributor is None:
        contributors = params.getlist('contributors')
        contributor = contributors[0] if contributors else None
    try:
        return int(contributor)
    except (TypeError, ValueError):
        return None


def _spotlight_config(contributor_id):
    """The contributor's embed config, if it shows Spotlight data."""
    from api.models.embed_config import EmbedConfig

    if contributor_id is None:
        return None
    return EmbedConfig.objects.filter(
        contributor__id=contributor_id,
        contributor__embed_level=DELUXE_EMBED_LEVEL,
        show_spotlight=True,
    ).first()


def shown_spotlight_groups(config):
    """The groups a contributor has chosen to show, of those available."""
    if config is None or not config.show_spotlight:
        return []
    chosen = set(config.spotlight_groups or [])
    return [
        group for group in available_spotlight_groups()
        if group['uuid'] in chosen
    ]


def spotlight_facility_ids(groups):
    """
    The ids of the facilities with data in any of `groups`, as a queryset
    of FacilityIndex ids. Matches nothing when there are no groups.
    """
    from api.models.facility.facility_index import FacilityIndex

    field_names = [
        name for group in groups for name in group['field_names']
    ]
    if not field_names:
        return FacilityIndex.objects.none().values('id')
    contributor_ids = {
        contributor_id
        for group in groups
        for contributor_id in group['contributor_ids']
    }
    return apply_partner_fields_or_filter(
        FacilityIndex.objects.all(), field_names, list(contributor_ids)
    ).values('id')


def _embed_shown_groups(params):
    """The groups shown on the embedded map being asked about, if any."""
    if params.get('embed') != '1':
        return []
    return shown_spotlight_groups(
        _spotlight_config(_embed_contributor_id(params))
    )


def apply_embed_spotlight_filter(facilities_qs, params):
    """
    Narrow a Facility or FacilityIndex queryset to the facilities with
    Spotlight data, when an embedded map asks for that. A map whose
    contributor does not offer the filter, or a group they do not show,
    matches nothing, so the filter cannot be used to probe partner data.
    """
    choice = params.get(EMBED_SPOTLIGHT_PARAM)
    if params.get('embed') != '1' or not choice:
        return facilities_qs

    config = _spotlight_config(_embed_contributor_id(params))
    groups = shown_spotlight_groups(config)
    if config is None or not config.spotlight_filter:
        groups = []
    elif choice != ANY_SPOTLIGHT:
        groups = [group for group in groups if group['uuid'] == choice]
    return facilities_qs.filter(id__in=spotlight_facility_ids(groups))


def embed_has_spotlight(params, only_when_highlighted=False):
    """
    For an embedded map that shows Spotlight data: an expression that is
    true for a facility with data in a group the contributor shows. None
    when the map shows none (or, with `only_when_highlighted`, does not
    ring those facilities on the map).
    """
    if params.get('embed') != '1':
        return None
    config = _spotlight_config(_embed_contributor_id(params))
    groups = shown_spotlight_groups(config)
    if not groups:
        return None
    if only_when_highlighted and not config.spotlight_highlight:
        return None
    return Exists(spotlight_facility_ids(groups).filter(id=OuterRef('id')))


def embed_spotlight_field_names(params):
    """
    The partner fields an embedded map may show on a facility's details:
    those in the groups its contributor shows. Empty for any other request.
    """
    return {
        name
        for group in _embed_shown_groups(params)
        for name in group['field_names']
    }


def _contributor_facility_ids(contributor):
    from api.models.facility.facility_list_item import FacilityListItem

    return FacilityListItem.objects.filter(
        source__contributor_id=contributor.id,
        source__is_active=True,
        facility__isnull=False,
    ).values('facility_id')


def _count(contributor, groups):
    return (
        spotlight_facility_ids(groups)
        .filter(id__in=_contributor_facility_ids(contributor))
        .count()
    )


def spotlight_for_visitors(contributor):
    """
    What a visitor's embedded map needs to show Spotlight data: whether to
    ring facilities and offer the filter, and the groups shown, each with
    the number of the contributor's facilities that have data in it. None
    when the contributor does not show Spotlight data.
    """
    config = contributor.embed_config
    if contributor.embed_level != DELUXE_EMBED_LEVEL:
        return None
    groups = shown_spotlight_groups(config)
    if not groups:
        return None
    return {
        'highlight': config.spotlight_highlight,
        'filter': config.spotlight_filter,
        'count': _count(contributor, groups),
        'groups': [
            {
                'uuid': group['uuid'],
                'name': group['name'],
                'count': _count(contributor, [group]),
                'field_names': group['field_names'],
            }
            for group in groups
        ],
    }


def spotlight_for_settings(contributor):
    """
    What the Embed settings screen needs to offer Spotlight: every group
    available, each with the number of the contributor's facilities that
    have data in it, how many facilities have any, and how many there are.
    """
    groups = available_spotlight_groups()
    return {
        'total': _contributor_facility_ids(contributor).distinct().count(),
        'count': _count(contributor, groups),
        'groups': [
            {
                'uuid': group['uuid'],
                'name': group['name'],
                'count': _count(contributor, [group]),
            }
            for group in groups
        ],
    }

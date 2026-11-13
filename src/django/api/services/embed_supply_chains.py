"""
Supply chains a contributor puts together from their own facilities, for
their embedded map: checking one before it is saved, and preparing the
published ones for visitors.
"""
from countries.lib.countries import COUNTRY_NAMES
from django.db.models.fields.json import KeyTextTransform
from rest_framework.exceptions import ValidationError

from api.models.embed_supply_chain import EmbedSupplyChain
from api.models.facility.facility import Facility
from api.models.facility.facility_list_item import FacilityListItem

MAX_STAGE_LENGTH = 60


def contributor_facility_ids(contributor_id, os_ids):
    """Which of `os_ids` are facilities this contributor has contributed."""
    return set(
        FacilityListItem.objects.filter(
            source__contributor_id=contributor_id,
            source__is_active=True,
            facility_id__in=os_ids,
        ).values_list('facility_id', flat=True)
    )


def _has_loop(links):
    """Whether following "supplies" links ever leads back to the start."""
    customers = {}
    for supplier, customer in links:
        customers.setdefault(supplier, []).append(customer)

    visiting, done = set(), set()

    def visit(os_id):
        if os_id in done:
            return False
        if os_id in visiting:
            return True
        visiting.add(os_id)
        looped = any(visit(next_id) for next_id in customers.get(os_id, []))
        visiting.discard(os_id)
        done.add(os_id)
        return looped

    return any(visit(os_id) for os_id in list(customers))


def validate_chain(contributor_id, nodes, links):
    """
    Check a supply chain's locations and links, and return them cleaned.
    Every location must be one of the contributor's own facilities, every
    link must join two locations in the chain, and the links must not loop.
    """
    if not isinstance(nodes, list) or not isinstance(links, list):
        raise ValidationError('Locations and links must be lists.')
    if len(nodes) > EmbedSupplyChain.MAX_NODES:
        raise ValidationError(
            'A supply chain can have at most {} locations.'.format(
                EmbedSupplyChain.MAX_NODES
            )
        )

    clean_nodes, seen = [], set()
    for node in nodes:
        os_id = node.get('os_id') if isinstance(node, dict) else None
        if not isinstance(os_id, str) or not os_id:
            raise ValidationError('Each location needs an OS ID.')
        if os_id in seen:
            raise ValidationError(
                'A location can only be in a supply chain once.'
            )
        seen.add(os_id)
        stage = str(node.get('stage') or '')[:MAX_STAGE_LENGTH]
        clean_nodes.append({'os_id': os_id, 'stage': stage})

    missing = seen - contributor_facility_ids(contributor_id, seen)
    if missing:
        raise ValidationError(
            'These are not among your facilities: {}.'.format(
                ', '.join(sorted(missing))
            )
        )

    clean_links, seen_links = [], set()
    for link in links:
        if not isinstance(link, (list, tuple)) or len(link) != 2:
            raise ValidationError('Each link joins two locations.')
        supplier, customer = link
        if supplier not in seen or customer not in seen:
            raise ValidationError(
                'A link can only join locations in the supply chain.'
            )
        if supplier == customer:
            raise ValidationError('A location cannot supply itself.')
        if (supplier, customer) in seen_links:
            continue
        seen_links.add((supplier, customer))
        clean_links.append([supplier, customer])

    if _has_loop(clean_links):
        raise ValidationError('The links in a supply chain cannot loop.')

    return clean_nodes, clean_links


def _tier_values(contributor, os_ids):
    """Each facility's value in the field the contributor colors markers by."""
    config = contributor.embed_config
    column = config.color_by_field if config else None
    if not column or not os_ids:
        return {}
    rows = (
        FacilityListItem.objects.filter(
            source__contributor_id=contributor.id,
            source__is_active=True,
            facility_id__in=os_ids,
        )
        .annotate(embed_value=KeyTextTransform(column, 'raw_json'))
        .exclude(embed_value__isnull=True)
        .exclude(embed_value='')
        .order_by('id')
        .values_list('facility_id', 'embed_value')
    )
    return dict(rows)


def contributor_locations(contributor):
    """
    Every facility the contributor has contributed, as the map in the
    builder needs it: name, position, and the value of the field the
    contributor colors markers by (their tier), used to suggest which way
    a link runs.
    """
    os_ids = list(
        FacilityListItem.objects.filter(
            source__contributor_id=contributor.id,
            source__is_active=True,
            facility_id__isnull=False,
        )
        .values_list('facility_id', flat=True)
        .distinct()
    )
    tiers = _tier_values(contributor, os_ids)
    return [
        {
            'os_id': os_id,
            'name': name,
            'country_name': COUNTRY_NAMES.get(country_code, ''),
            'lat': location.y,
            'lng': location.x,
            'tier': tiers.get(os_id),
        }
        for os_id, name, country_code, location in Facility.objects.filter(
            id__in=os_ids
        )
        .order_by('name')
        .values_list('id', 'name', 'country_code', 'location')
    ]


def published_supply_chains(contributor):
    """
    The contributor's published supply chains as a visitor's embedded map
    needs them: each location with its name, place and position. A location
    whose facility no longer exists is left out, along with its links.
    """
    chains = list(
        EmbedSupplyChain.objects.filter(
            contributor=contributor, is_published=True
        )
    )
    os_ids = {node['os_id'] for chain in chains for node in chain.nodes}
    facilities = {
        facility.id: facility
        for facility in Facility.objects.filter(id__in=os_ids)
    }
    tiers = _tier_values(contributor, os_ids)

    published = []
    for chain in chains:
        nodes = []
        for node in chain.nodes:
            facility = facilities.get(node['os_id'])
            if facility is None:
                continue
            nodes.append({
                'os_id': facility.id,
                'name': facility.name,
                'address': facility.address,
                'country_name': COUNTRY_NAMES.get(facility.country_code, ''),
                'lat': facility.location.y,
                'lng': facility.location.x,
                'stage': node.get('stage', ''),
                'tier': tiers.get(facility.id),
            })
        kept = {node['os_id'] for node in nodes}
        published.append({
            'id': chain.id,
            'name': chain.name,
            'description': chain.description,
            'product_url': chain.product_url,
            'color': chain.color,
            'nodes': nodes,
            'links': [
                link for link in chain.links
                if link[0] in kept and link[1] in kept
            ],
        })
    return published

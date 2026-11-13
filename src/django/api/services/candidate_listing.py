"""
The paged candidate list (OSDEV-3754).

Backs the list mode of ``GET /api/v1/production-locations/candidates/``:
every live candidate, filtered, sorted and paged, each row annotated
with how many confirmed facilities sit within the suggestion radius and
how far the nearest one is.

Nearby figures are computed on read, like the suggested matches on the
detail endpoint (see ``candidate_matches.py``): there is no table to
keep in step with ingest, merges or retirements, and the GiST index on
``api_facility.location`` answers each per-row lookup. They are costed
in two tiers so the common request stays cheap:

* ``nearby_count`` / ``nearest_m`` are annotated on the *whole* filtered
  set only when the request sorts or filters on them; otherwise the page
  is cut first and only its rows are annotated;
* the nearest facility's OS ID and name are always page-level.

Whole-set annotation costs one location-index probe per candidate
(measured on production with 16,370 candidates against 2.5M facilities:
0.11 ms per probe, 1.9 s per request with every page warm). Rather than
pay that on every page of a nearby-sorted list, the ordered OS IDs of such
a request are kept in the ``candidate_lists`` cache (memcached, shared by
every Django process) for ``CANDIDATE_LIST_ORDER_CACHE_SECONDS``, keyed
by every filter except ``page`` / ``limit`` and by the settings the
order depends on. The rows of the requested page are always fetched live
and re-checked against the column filters, so state and tally are
current and a row that stopped being a candidate (or left the filters)
is dropped; only membership in a nearby-sorted, state-filtered set can
lag by the cache window after a vote, and the ``count`` can include such
a dropped row. memcached's default item cap is 1 MB, about 50k ids; a
list that does not fit is not cached and a warning is logged.

Alternative kept in reserve (not built): store ``nearby_count``,
``nearest_m`` and the nearest facility's id per candidate in a small
table keyed by candidate, written by ``ingest_satellite_detections`` and
a ``refresh_candidate_nearby`` management command (one set-based
``UPDATE`` over the same two-filter join), and join it here with
``select_related``. That makes every sort a plain column order with no
cache window, at the price of a migration and of figures that are stale
about facilities confirmed after the last refresh. Worth doing if the
candidate set grows to the point where the cached query itself (linear
in the number of candidates) becomes a problem, around 50k candidates.
"""
import hashlib
import json
import logging
import math

from django.conf import settings
from django.contrib.gis.db.models import PointField
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Polygon
from django.contrib.gis.measure import D
from django.core.cache import caches
from django.core.paginator import EmptyPage, Paginator
from django.db.models import (
    ExpressionWrapper,
    F,
    FloatField,
    IntegerField,
    OuterRef,
    Q,
    Subquery,
)

from api.models.facility.facility import Facility
from api.serializers.v1.candidates_list_query_param_serializer import (
    NEARBY_SORT_FIELDS,
)
from api.services import candidate_validation
from api.services.candidate_matches import METRES_PER_DEGREE

logger = logging.getLogger(__name__)

# ``candidate_matches._degree_radius`` widens the pre-filter by the
# point's own latitude. That is not possible here: the radius cannot
# depend on the outer row's latitude inside a correlated subquery without
# losing the index, so it is fixed at the widening for this latitude.
# 75 degrees covers every populated place; above it the list can report
# fewer nearby facilities than the detail endpoint's suggested matches.
PREFILTER_MAX_LATITUDE = 75.0


def _prefilter_degree_radius(radius_m):
    """``radius_m`` metres of longitude as degrees at the fixed latitude."""
    return (
        radius_m / METRES_PER_DEGREE
        / math.cos(math.radians(PREFILTER_MAX_LATITUDE))
    )


def _outer_location():
    """
    The outer candidate row's point, typed so the GIS functions and
    lookups can see it is a geometry (a bare ``OuterRef`` carries no
    output field and ``Distance`` refuses it).
    """
    return ExpressionWrapper(
        OuterRef('location'), output_field=PointField(srid=4326)
    )


class SubqueryCount(Subquery):
    """``(SELECT count(*) FROM (<subquery>) _count)``."""
    template = '(SELECT count(*) FROM (%(subquery)s) _count)'
    output_field = IntegerField()


def _nearby_facilities(radius_m):
    """
    Confirmed facilities within ``radius_m`` of the outer candidate row.
    Two filters on purpose, as in ``candidate_matches``: ``dwithin`` in
    degrees is what the GiST index answers, ``distance_lte`` in metres
    trims that box to the circle. ``Facility.objects`` excludes
    candidates, so a candidate never counts another candidate.
    """
    return Facility.objects.filter(
        location__dwithin=(
            _outer_location(), _prefilter_degree_radius(radius_m)
        ),
        location__distance_lte=(_outer_location(), D(m=radius_m)),
    )


def _nearest(radius_m):
    """The nearby facilities, closest first, with ``distance`` annotated."""
    return (
        _nearby_facilities(radius_m)
        .annotate(distance=Distance('location', _outer_location()))
        .order_by('distance', 'id')
    )


def annotate_nearby_count_and_distance(queryset, radius_m=None):
    """
    Annotate each candidate with ``nearby_count`` and ``nearest_m``: two
    correlated subqueries per row, each answered by the location index.
    """
    if radius_m is None:
        radius_m = settings.CANDIDATE_SUGGESTION_RADIUS_M
    return queryset.annotate(
        nearby_count=SubqueryCount(
            _nearby_facilities(radius_m).order_by().values('id')
        ),
        nearest_m=Subquery(
            _nearest(radius_m).values('distance')[:1],
            output_field=FloatField(),
        ),
    )


def annotate_nearest_facility(queryset, radius_m=None):
    """
    Annotate ``nearest_os_id`` and ``nearest_name``; page-level only, as
    these are two more probes per row and only the page needs them.
    """
    if radius_m is None:
        radius_m = settings.CANDIDATE_SUGGESTION_RADIUS_M
    return queryset.annotate(
        nearest_os_id=Subquery(_nearest(radius_m).values('id')[:1]),
        nearest_name=Subquery(_nearest(radius_m).values('name')[:1]),
    )


def _bbox_filter(bbox):
    """
    Candidates whose polygon, or point when there is no polygon,
    intersects the ``(min_lng, min_lat, max_lng, max_lat)`` box; the
    map mode's rule.
    """
    envelope = Polygon.from_bbox(bbox)
    envelope.srid = 4326
    return (
        Q(polygon__intersects=envelope)
        | Q(polygon__isnull=True, location__intersects=envelope)
    )


def _state_filter(states):
    """
    A ``Q`` selecting the candidates whose derived validation state is in
    ``states``. State is never stored, so it is derived here from the
    tallies of every candidate that has at least one vote; a candidate
    with no votes is ``unverified`` without appearing in that map.
    """
    voted = candidate_validation.voted_tallies()
    derived = {
        os_id: candidate_validation.public_state(
            candidate_validation.derive_state(vote_tally)
        )
        for os_id, vote_tally in voted.items()
    }
    wanted = set(states)
    selected = [
        os_id for os_id, state in derived.items() if state in wanted
    ]
    condition = Q(id__in=selected)
    if candidate_validation.UNVERIFIED in wanted:
        not_unverified = [
            os_id for os_id, state in derived.items()
            if state != candidate_validation.UNVERIFIED
        ]
        condition |= ~Q(id__in=not_unverified)
    return condition


def _ordering(sort):
    """``order_by`` arguments for a validated ``sort`` value."""
    descending = sort.startswith('-')
    field = sort[1:] if descending else sort
    if field == 'id':
        return ('-id',) if descending else ('id',)
    expression = F(field)
    # Candidates without a confirmed neighbour have nearest_m NULL; they
    # belong at the end whichever way the distance is sorted.
    primary = (
        expression.desc(nulls_last=True)
        if descending else expression.asc(nulls_last=True)
    )
    return (primary, 'id')


def _column_filtered(params):
    """
    Live candidates narrowed by the filters that are plain columns (and
    the bbox): everything in ``params`` except ``state``, which is derived
    from votes, and ``has_nearby``, which needs the whole-set annotation.
    Applied to the filtered set and again to the page rows, so a row that
    left the set after its ordering was cached is dropped rather than
    served (see ``list_candidates``).
    """
    queryset = Facility.including_candidates.filter(is_candidate=True)
    bbox = params.get('bbox')
    if bbox:
        queryset = queryset.filter(_bbox_filter(bbox))
    if params.get('confidence_min') is not None:
        queryset = queryset.filter(confidence__gte=params['confidence_min'])
    if params.get('confidence_max') is not None:
        queryset = queryset.filter(confidence__lte=params['confidence_max'])
    if params.get('country'):
        queryset = queryset.filter(country_code__in=params['country'])
    if params.get('source'):
        queryset = queryset.filter(source=params['source'])
    return queryset


def needs_whole_set_nearby(params):
    """
    Whether validated list ``params`` sort or filter on the nearby
    figures, which means annotating the whole filtered set (one
    location-index probe per candidate, ~1.9 s on production) before the
    page can be cut. The view requires a login for these requests: the
    order cache only helps an identical parameter set, so an anonymous
    caller varying one filter per request would run the full query every
    time, and at the 100/minute anonymous burst rate that is about three
    database-seconds per second from one address.
    """
    sort = (params.get('sort') or 'id').lstrip('-')
    return sort in NEARBY_SORT_FIELDS or params.get('has_nearby') is not None


def candidate_queryset(params):
    """
    ``(queryset, ordered_by_nearby)``: the filtered, ordered queryset for
    validated list ``params`` (the ``validated_data`` of
    ``CandidatesListQueryParamSerializer``), not yet paged, and whether
    it carries the whole-set nearby annotation (the expensive path whose
    ordering ``list_candidates`` caches).
    """
    queryset = _column_filtered(params)
    if params.get('state'):
        queryset = queryset.filter(_state_filter(params['state']))

    sort = params.get('sort') or 'id'
    has_nearby = params.get('has_nearby')
    needs_nearby_on_set = needs_whole_set_nearby(params)
    if needs_nearby_on_set:
        queryset = annotate_nearby_count_and_distance(queryset)
        if has_nearby is True:
            queryset = queryset.filter(nearby_count__gt=0)
        elif has_nearby is False:
            queryset = queryset.filter(nearby_count=0)

    return queryset.order_by(*_ordering(sort)), needs_nearby_on_set


class PageNotFound(Exception):
    """``page`` is past the last page of the filtered set."""


ORDER_CACHE_ALIAS = 'candidate_lists'
# Bump when the ordering or filter semantics change, so a deploy never
# serves an id list computed by the previous code.
ORDER_CACHE_VERSION = 1


# The settings the ordering depends on. memcached outlives a deploy, so a
# changed radius or vote threshold must miss the entries computed under
# the old value rather than serve them for the rest of the window.
ORDER_CACHE_SETTINGS = (
    'CANDIDATE_SUGGESTION_RADIUS_M',
    'CANDIDATE_VOTE_THRESHOLD',
    'CANDIDATE_CONFIRM_MARGIN',
    'CANDIDATE_RETIRE_MARGIN',
)


def _order_cache_key(params):
    """The cache key of a request's ordered id list: every filter and the
    sort, but not the page or its size, plus the settings the order and
    the state filter are computed under."""
    relevant = {
        key: value for key, value in sorted(params.items())
        if key not in ('page', 'limit') and value is not None
    }
    relevant['settings'] = {
        name: getattr(settings, name) for name in ORDER_CACHE_SETTINGS
    }
    digest = hashlib.sha256(
        json.dumps(relevant, sort_keys=True, default=list).encode()
    ).hexdigest()
    return f'order:v{ORDER_CACHE_VERSION}:{digest}'


def _ordered_ids_cached(params, queryset):
    """
    The whole ordered id list for a nearby-sorted or nearby-filtered
    request, from the cache when a request with the same filters and
    sort ran within ``CANDIDATE_LIST_ORDER_CACHE_SECONDS``.
    """
    ttl = settings.CANDIDATE_LIST_ORDER_CACHE_SECONDS
    if ttl <= 0:
        return list(queryset.values_list('id', flat=True))
    cache = caches[ORDER_CACHE_ALIAS]
    key = _order_cache_key(params)
    ids = cache.get(key)
    if ids is None:
        ids = list(queryset.values_list('id', flat=True))
        _store_order(cache, key, ids, ttl)
    return ids


def _store_order(cache, key, ids, ttl):
    """
    Cache the ordered id list and check it landed. memcached stores one
    item of at most 1 MB by default (about 50k pickled ids); over that it
    refuses the set and every page of the request silently pays the
    whole-set query again. That failure is logged so it shows up as a
    log line rather than as an unexplained latency regression.
    """
    try:
        cache.set(key, ids, ttl)
        stored = cache.get(key) is not None
    except Exception:  # the backend refused the item (too large)
        stored = False
    if not stored:
        logger.warning(
            'Candidate list order %s (%d ids) was not cached; every page '
            'of this request will run the whole-set nearby query.',
            key,
            len(ids),
        )


def _page_slice(ids, page, limit):
    """``(page ids, total)`` from a cached ordering; 404 past the end."""
    start = (page - 1) * limit
    if start >= len(ids) and page > 1:
        raise PageNotFound()
    return ids[start:start + limit], len(ids)


def list_candidates(params):
    """
    Resolve one page: ``(rows, total_count)``. Each row is a ``Facility``
    carrying ``nearby_count``, ``nearest_m``, ``nearest_os_id`` and
    ``nearest_name`` attributes. Raises ``PageNotFound`` for a page past
    the end (page 1 of an empty set is fine and returns no rows).
    """
    queryset, ordered_by_nearby = candidate_queryset(params)
    if ordered_by_nearby:
        page_ids, total = _page_slice(
            _ordered_ids_cached(params, queryset),
            params['page'],
            params['limit'],
        )
    else:
        paginator = Paginator(
            queryset.values_list('id', flat=True), params['limit']
        )
        try:
            page_ids = list(paginator.page(params['page']).object_list)
        except EmptyPage:
            if params['page'] != 1:
                raise PageNotFound()
            page_ids = []
        total = paginator.count
    # The cached ordering is trusted for order and count, not for
    # membership: a row promoted out of candidacy or edited out of the
    # column filters since the order was cached is dropped here.
    rows = _column_filtered(params).filter(id__in=page_ids)
    rows = annotate_nearby_count_and_distance(rows)
    rows = annotate_nearest_facility(rows)
    by_id = {row.id: row for row in rows}
    # Re-apply the page order: the id__in fetch has none of its own.
    # A candidate retired or filtered out since the ordering was cached
    # is simply absent.
    ordered = [by_id[os_id] for os_id in page_ids if os_id in by_id]
    return ordered, total

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
by every filter except ``page`` / ``limit``. The rows of the requested
page are always fetched live, so state and tally are current; only
membership in a nearby-sorted, state-filtered set can lag by the cache
window after a vote.

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

# A degree radius that covers CANDIDATE_SUGGESTION_RADIUS_M metres of
# longitude anywhere up to this latitude; the exact metre filter trims the
# overshoot. 75 degrees covers every populated place. A fixed value is
# needed because the pre-filter radius cannot depend on the outer row's
# latitude inside a correlated subquery without losing the index.
PREFILTER_MAX_LATITUDE = 75.0
METRES_PER_DEGREE = 111_320.0


def _degree_radius(radius_m):
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
        location__dwithin=(_outer_location(), _degree_radius(radius_m)),
        location__distance_lte=(_outer_location(), D(m=radius_m)),
    )


def _nearest(radius_m):
    return (
        _nearby_facilities(radius_m)
        .annotate(distance=Distance('location', _outer_location()))
        .order_by('distance', 'id')
    )


def annotate_nearby_count_and_distance(queryset, radius_m=None):
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
    if radius_m is None:
        radius_m = settings.CANDIDATE_SUGGESTION_RADIUS_M
    return queryset.annotate(
        nearest_os_id=Subquery(_nearest(radius_m).values('id')[:1]),
        nearest_name=Subquery(_nearest(radius_m).values('name')[:1]),
    )


def _bbox_filter(bbox):
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


def candidate_queryset(params):
    """
    ``(queryset, ordered_by_nearby)``: the filtered, ordered queryset for
    validated list ``params`` (the ``validated_data`` of
    ``CandidatesListQueryParamSerializer``), not yet paged, and whether
    it carries the whole-set nearby annotation (the expensive path whose
    ordering ``list_candidates`` caches).
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
    if params.get('state'):
        queryset = queryset.filter(_state_filter(params['state']))

    sort = params.get('sort') or 'id'
    sort_field = sort.lstrip('-')
    has_nearby = params.get('has_nearby')
    needs_nearby_on_set = (
        sort_field in NEARBY_SORT_FIELDS or has_nearby is not None
    )
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


def _order_cache_key(params):
    """The cache key of a request's ordered id list: every filter and the
    sort, but not the page or its size."""
    relevant = {
        key: value for key, value in sorted(params.items())
        if key not in ('page', 'limit') and value is not None
    }
    digest = hashlib.sha1(
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
        cache.set(key, ids, ttl)
    return ids


def _page_slice(ids, page, limit):
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
    rows = Facility.including_candidates.filter(id__in=page_ids)
    rows = annotate_nearby_count_and_distance(rows)
    rows = annotate_nearest_facility(rows)
    by_id = {row.id: row for row in rows}
    # Re-apply the page order: the id__in fetch has none of its own.
    # A candidate retired since the ordering was cached is simply absent.
    ordered = [by_id[os_id] for os_id in page_ids if os_id in by_id]
    return ordered, total

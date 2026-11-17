"""
Proximity suggestions for a candidate facility (OSDEV-3244).

A candidate is an unnamed satellite detection; the most useful thing a
human reviewer can see next to it is the confirmed facilities that
already sit at or near the same spot. Suggestions are computed on read
rather than stored: there is no table to migrate, the answer is always
current (a facility confirmed, merged or deleted after ingest is
reflected immediately) and the query is backed by the GiST index on
``api_facility.location``.

Only confirmed facilities are ever suggested. The query runs on
``Facility.objects`` whose default manager excludes ``is_candidate=True``
rows, so a candidate can never be suggested for another candidate.
"""
import math

from django.conf import settings
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D

from api.models.facility.facility import Facility

# Metres per degree of latitude (and of longitude at the equator). Used
# only to turn the metre radius into the degree radius the index-backed
# ``dwithin`` pre-filter needs on a geodetic geometry column.
#
# Deliberately a little under the true figure. ``ST_DistanceSphere``,
# which the exact filter uses, measures on a sphere where a degree is
# about 111,195 m; the WGS 84 equatorial value (111,320) is larger than
# that, which made the pre-filter box a fraction too small and dropped
# a facility between roughly 499.4 m and 500 m of a 500 m radius. A
# value below the sphere's keeps the box over-inclusive, which is all a
# pre-filter has to be.
METRES_PER_DEGREE = 111_000.0

# Floor of the latitude cosine, so the widening stays finite at a pole.
# Shared with the list's per-row radius (``candidate_listing``), which
# must widen exactly as this module does for the two to agree.
MIN_COS_LATITUDE = 0.01


def _degree_radius(point, radius_m):
    """
    A degree radius that is never smaller than ``radius_m`` in any
    direction at ``point``'s latitude. A degree of longitude shrinks with
    the cosine of the latitude, so the pre-filter is widened to match;
    the exact metre filter afterwards removes the overshoot.
    """
    cos_lat = math.cos(math.radians(point.y))
    return radius_m / METRES_PER_DEGREE / max(cos_lat, MIN_COS_LATITUDE)


def suggested_matches_for_point(
    point, radius_m=None, limit=None, exclude_os_id=None
):
    """
    Confirmed facilities within ``radius_m`` metres of ``point``, nearest
    first, as a list of ``{"os_id", "name", "address", "distance_m"}``.

    ``radius_m`` defaults to ``settings.CANDIDATE_SUGGESTION_RADIUS_M`` and
    ``limit`` to ``settings.CANDIDATE_SUGGESTION_LIMIT``. ``exclude_os_id``
    drops one facility (the one being looked at) from the result.

    Two filters are applied on purpose. ``location__dwithin`` with a
    degree radius is what PostGIS can answer from the GiST index on the
    geometry column (``ST_DWithin`` on a geometry expands the bounding
    box); ``distance_lte`` in metres (``ST_DistanceSphere``) then trims
    that over-inclusive box to the true circle.
    """
    if point is None:
        return []
    if radius_m is None:
        radius_m = settings.CANDIDATE_SUGGESTION_RADIUS_M
    if limit is None:
        limit = settings.CANDIDATE_SUGGESTION_LIMIT

    queryset = (
        Facility.objects
        .filter(location__dwithin=(point, _degree_radius(point, radius_m)))
        .filter(location__distance_lte=(point, D(m=radius_m)))
        .annotate(distance=Distance('location', point))
        .order_by('distance', 'id')
        .values_list('id', 'name', 'address', 'distance')
    )
    if exclude_os_id:
        queryset = queryset.exclude(id=exclude_os_id)
    return [
        {
            'os_id': os_id,
            'name': name,
            'address': address,
            'distance_m': round(distance.m, 1),
        }
        for os_id, name, address, distance in queryset[:limit]
    ]


def suggested_matches(candidate, radius_m=None, limit=None):
    """
    Confirmed facilities near ``candidate`` (a ``Facility``), nearest
    first; see :func:`suggested_matches_for_point` for the shape.

    ``candidate`` itself is never returned, so the helper is also safe to
    call on a facility that has since been promoted out of candidacy.
    """
    return suggested_matches_for_point(
        candidate.location,
        radius_m=radius_m,
        limit=limit,
        exclude_os_id=candidate.pk,
    )

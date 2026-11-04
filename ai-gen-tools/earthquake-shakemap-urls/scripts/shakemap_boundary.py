"""
Reference copy of the core geometry pipeline used in the earthquake-shakemap-urls
skill's template.ipynb. Not imported by the notebook itself (the notebook stays
fully self-contained so it can be shared/moved without this file) — use this
module for quick prototyping in a scratch script when tuning STRIP_WIDTH,
BUFFER, SIMPLIFY, or COORD_PRECISION before committing changes to the notebook.
See SKILL.md for the reasoning behind each step and the order they must run in.
"""
import heapq
import json
import math
import urllib.parse

import geopandas as gpd
import requests
from shapely.geometry import LineString, MultiPolygon, Polygon
from shapely.ops import nearest_points, unary_union

MAX_URL_LENGTH = 2000
COORD_PRECISION = 4
STRIP_WIDTH = 0.0001


def get_shakemap_contour_url(event_id, product="cont_mmi.json"):
    api_url = f"https://earthquake.usgs.gov/fdsnws/event/1/query?eventid={event_id}&format=geojson"
    r = requests.get(api_url)
    r.raise_for_status()
    data = r.json()
    shakemap = data["properties"]["products"]["shakemap"][0]
    return shakemap["contents"][f"download/{product}"]["url"]


def get_mmi_contours(event_id):
    r = requests.get(get_shakemap_contour_url(event_id))
    r.raise_for_status()
    return r.json()


def contour_geom_to_polygon(geometry):
    """Convert a USGS MMI contour ring (or set of rings) to a Polygon,
    correctly treating a ring nested inside another as a real hole (a
    localized low-intensity island) rather than blindly unioning it in as
    solid area."""
    if geometry["type"] == "LineString":
        coords = geometry["coordinates"]
        if coords[0] != coords[-1]:
            coords = coords + [coords[0]]
        return Polygon(coords)

    elif geometry["type"] == "MultiLineString":
        rings = []
        for ring in geometry["coordinates"]:
            if ring[0] != ring[-1]:
                ring = ring + [ring[0]]
            if len(ring) >= 4:
                p = Polygon(ring)
                if p.is_valid and not p.is_empty:
                    rings.append(p)
        if not rings:
            return None

        rings.sort(key=lambda p: p.area, reverse=True)
        result = None
        for p in rings:
            if result is not None and p.within(result):
                result = result.difference(p)
            else:
                result = p if result is None else unary_union([result, p])
        return result

    return None


def dissolve_multipolygon(geom, width=STRIP_WIDTH):
    """Bridge every piece of a MultiPolygon to the single largest piece
    (star topology) with a minimal-width connector strip, so the result is
    always one Polygon. Run AFTER buffer/simplify, not on raw geometry."""
    if geom.geom_type != "MultiPolygon":
        return geom

    pieces = sorted(geom.geoms, key=lambda g: g.area, reverse=True)
    hub = pieces[0]
    parts = [hub]

    for piece in pieces[1:]:
        p1, p2 = nearest_points(hub, piece)
        dx, dy = p2.x - p1.x, p2.y - p1.y
        length = math.hypot(dx, dy)
        if length == 0:
            parts.append(piece)
            continue
        dx, dy = dx / length, dy / length
        p1_ext = (p1.x - dx * width, p1.y - dy * width)
        p2_ext = (p2.x + dx * width, p2.y + dy * width)
        strip = LineString([p1_ext, p2_ext]).buffer(width / 2, cap_style=2)
        parts.append(strip)
        parts.append(piece)

    dissolved = unary_union(parts)
    if dissolved.geom_type != "Polygon":
        print(f"WARNING: dissolve left a {dissolved.geom_type} — widen STRIP_WIDTH")
    return dissolved


def remove_holes(geom):
    """Fill in interior rings. Run this AFTER dissolve_multipolygon — the
    connector-strip unions in dissolve can themselves introduce new
    artifact holes that must also get cleaned up."""
    if geom.geom_type == "Polygon":
        return Polygon(geom.exterior)
    elif geom.geom_type == "MultiPolygon":
        return MultiPolygon([Polygon(p.exterior) for p in geom.geoms])
    return geom


def _vw_simplify_ring(coords, tolerance):
    """Visvalingam-Whyatt simplification of a single closed ring
    (coords[0] == coords[-1]): iteratively removes the vertex whose triangle
    with its two current neighbors has the smallest area, stopping once the
    smallest remaining area reaches tolerance^2."""
    pts = list(coords[:-1])
    n = len(pts)
    if n <= 3:
        return coords

    min_area = tolerance ** 2
    prev = [(i - 1) % n for i in range(n)]
    nxt = [(i + 1) % n for i in range(n)]
    alive = [True] * n

    def tri_area(i):
        ax, ay = pts[prev[i]]
        bx, by = pts[i]
        cx, cy = pts[nxt[i]]
        return abs((bx - ax) * (cy - ay) - (cx - ax) * (by - ay)) / 2.0

    heap = [(tri_area(i), i) for i in range(n)]
    heapq.heapify(heap)

    n_alive = n
    while heap and n_alive > 3:
        area, i = heapq.heappop(heap)
        if not alive[i]:
            continue
        current = tri_area(i)
        if current != area:
            heapq.heappush(heap, (current, i))
            continue
        if area >= min_area:
            break
        alive[i] = False
        n_alive -= 1
        p, nx = prev[i], nxt[i]
        nxt[p] = nx
        prev[nx] = p
        heapq.heappush(heap, (tri_area(p), p))
        heapq.heappush(heap, (tri_area(nx), nx))

    kept = [pts[i] for i in range(n) if alive[i]]
    kept.append(kept[0])
    return kept


def _vw_simplify_polygon(poly, tolerance):
    exterior = _vw_simplify_ring(list(poly.exterior.coords), tolerance)
    interiors = [_vw_simplify_ring(list(r.coords), tolerance) for r in poly.interiors]
    result = Polygon(exterior, interiors)
    if not result.is_valid:
        result = result.buffer(0)
    return result


def _vw_simplify_geom(geom, tolerance):
    if geom.geom_type == "Polygon":
        return _vw_simplify_polygon(geom, tolerance)
    elif geom.geom_type == "MultiPolygon":
        parts = [_vw_simplify_polygon(p, tolerance) for p in geom.geoms]
        return MultiPolygon(parts) if len(parts) > 1 else parts[0]
    return geom


def simplify_geom(geom, tolerance, method="douglas_peucker"):
    """Two interchangeable algorithms, named after their equivalents in
    ArcGIS Pro's Simplify Polygon tool (POINT_REMOVE and EFFECTIVE_AREA):
    "douglas_peucker" (shapely's built-in, GEOS-backed) or
    "visvalingam_whyatt" (this module's custom implementation — tends to
    preserve shape character better at aggressive tolerances, but retains
    more vertices per unit of tolerance)."""
    if method == "douglas_peucker":
        return geom.simplify(tolerance)
    elif method == "visvalingam_whyatt":
        return _vw_simplify_geom(geom, tolerance)
    else:
        raise ValueError(f"Unknown SIMPLIFY_METHOD: {method!r}")


def process_geom(raw_geom, buffer, simplify, method="douglas_peucker"):
    gdf = gpd.GeoDataFrame(geometry=[raw_geom], crs="EPSG:4326")
    buffered = gdf.buffer(buffer).iloc[0]
    simplified = simplify_geom(buffered, simplify, method)
    dissolved = dissolve_multipolygon(simplified)
    return remove_holes(dissolved)


def round_coordinates(geom_mapping, ndigits=COORD_PRECISION):
    def process(obj):
        if isinstance(obj[0], (int, float)):
            return [round(c, ndigits) for c in obj]
        return [process(o) for o in obj]
    geom_mapping = dict(geom_mapping)
    geom_mapping["coordinates"] = process(geom_mapping["coordinates"])
    return geom_mapping


def to_osh_url(raw_geom, buffer=0.1, simplify=0.01, method="douglas_peucker",
               max_len=MAX_URL_LENGTH, max_tries=15):
    def build(simp):
        processed = process_geom(raw_geom, buffer, simp, method)
        coords = json.loads(gpd.GeoSeries([processed]).to_json())["features"][0]["geometry"]
        coords = round_coordinates(coords)
        encoded = urllib.parse.quote(json.dumps(coords, separators=(",", ":")))
        url = f"https://opensupplyhub.org/facilities/?boundary={encoded}&sort_by=contributors_desc"
        return url, processed

    url, geom = build(simplify)
    tries = 0
    while len(url) > max_len and tries < max_tries:
        simplify *= 1.3
        url, geom = build(simplify)
        tries += 1

    if len(url) > max_len:
        print(f"WARNING: could not get URL under {max_len} chars after {max_tries} tries "
              f"(final length {len(url)}, simplify={simplify:.3f})")

    return url, geom

#!/usr/bin/env python3
"""
Build the default earthquake-shakemap-urls deliverable: a self-contained,
interactive HTML page (assets/template_interactive.html) with live
buffer/simplify sliders per MMI level, an overlaid real-USGS-contour
reference line, and a basemap for orientation.

Usage (edit the EVENTS/TITLE/etc. block below, or import and call build()):
    python3 build_interactive.py

No network access happens inside the generated page itself — this script
does all the fetching once, at build time, and embeds the results.
"""
import json
import os
import sys
import urllib.request

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_PATH = os.path.join(SKILL_DIR, "assets", "template_interactive.html")
TURF_JS_PATH = os.path.join(SKILL_DIR, "assets", "turf.min.js")
BASEMAP_PATH = os.path.join(SKILL_DIR, "assets", "ne_countries_110m.min.geojson")


def fetch_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "earthquake-shakemap-urls-skill"})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))


def get_cont_mmi(event_id):
    api_url = f"https://earthquake.usgs.gov/fdsnws/event/1/query?eventid={event_id}&format=geojson"
    data = fetch_json(api_url)
    shakemap = data["properties"]["products"]["shakemap"][0]
    contour_url = shakemap["contents"]["download/cont_mmi.json"]["url"]
    print(f"Fetching: {contour_url}")
    return fetch_json(contour_url)


def combined_bbox(contour_fcs):
    """Bounding box across every ring of every level of every event, in
    plain [minLon, minLat, maxLon, maxLat] — used only to crop the basemap,
    so this stays a simple flat min/max rather than pulling in shapely."""
    minx = miny = float("inf")
    maxx = maxy = float("-inf")
    for fc in contour_fcs:
        for feature in fc["features"]:
            for ring in feature["geometry"]["coordinates"]:
                for lon, lat in ring:
                    minx, maxx = min(minx, lon), max(maxx, lon)
                    miny, maxy = min(miny, lat), max(maxy, lat)
    return minx, miny, maxx, maxy


def crop_basemap(bbox, pad_frac=0.2, round_digits=3):
    """Filter the vendored world countries file down to whichever countries'
    own bounding boxes intersect the (padded) earthquake region, and round
    coordinates — keeps the embedded basemap small and specific to this
    event rather than shipping the whole world every time."""
    minx, miny, maxx, maxy = bbox
    w, h = maxx - minx, maxy - miny
    pad = max(w, h) * pad_frac
    minx, miny, maxx, maxy = minx - pad, miny - pad, maxx + pad, maxy + pad

    with open(BASEMAP_PATH, "r", encoding="utf-8") as f:
        world = json.load(f)

    def ring_bbox(coords_tree):
        bx0 = by0 = float("inf")
        bx1 = by1 = float("-inf")
        stack = [coords_tree]
        while stack:
            node = stack.pop()
            if isinstance(node[0], (int, float)):
                lon, lat = node[0], node[1]
                bx0, bx1 = min(bx0, lon), max(bx1, lon)
                by0, by1 = min(by0, lat), max(by1, lat)
            else:
                stack.extend(node)
        return bx0, by0, bx1, by1

    def round_coords(node, n):
        if isinstance(node[0], (int, float)):
            return [round(node[0], n), round(node[1], n)]
        return [round_coords(c, n) for c in node]

    kept = []
    for feature in world["features"]:
        fx0, fy0, fx1, fy1 = ring_bbox(feature["geometry"]["coordinates"])
        if fx1 < minx or fx0 > maxx or fy1 < miny or fy0 > maxy:
            continue
        feature = {
            "type": "Feature",
            "properties": {"name": feature["properties"].get("name")},
            "geometry": {
                "type": feature["geometry"]["type"],
                "coordinates": round_coords(feature["geometry"]["coordinates"], round_digits),
            },
        }
        kept.append(feature)

    print(f"Basemap: kept {len(kept)}/{len(world['features'])} countries intersecting the padded event region")
    return {"type": "FeatureCollection", "features": kept}


def build(events, output_path, title, eyebrow, h1, subhead_html, verify_links_html,
          dropped_note_html="", footer_html=""):
    """
    events: dict of {display_name: usgs_event_id}
    output_path: where to write the final .html
    title / eyebrow / h1 / subhead_html: header content (subhead_html may contain inline HTML)
    verify_links_html: HTML for the "verify before trusting" callout box, one
        <p>...</p> per event is typical — MUST include each event's
        eventpage/shakemap/intensity link
    dropped_note_html: optional <div class="dropped-note">...</div> block,
        or "" if nothing was excluded (with the interactive tool, prefer NOT
        excluding levels preemptively — see SKILL.md troubleshooting)
    footer_html: short attribution sentence(s); the template appends the
        legend explanation automatically
    """
    contour_fcs = {}
    for name, event_id in events.items():
        contour_fcs[name] = get_cont_mmi(event_id)

    bbox = combined_bbox(list(contour_fcs.values()))
    basemap = crop_basemap(bbox)

    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        template = f.read()
    with open(TURF_JS_PATH, "r", encoding="utf-8") as f:
        turf_js = f.read()

    page = template
    page = page.replace("__TITLE__", title)
    page = page.replace("__EYEBROW__", eyebrow)
    page = page.replace("__H1__", h1)
    page = page.replace("__SUBHEAD__", subhead_html)
    page = page.replace("__VERIFY_LINKS_HTML__", verify_links_html)
    page = page.replace("__DROPPED_NOTE_HTML__", dropped_note_html)
    page = page.replace("__FOOTER_HTML__", footer_html)
    page = page.replace("__TURF_JS__", turf_js)
    page = page.replace("__BASEMAP_JSON__", json.dumps(basemap, separators=(",", ":")))
    page = page.replace("__CONTOURS_JS__", json.dumps(contour_fcs, separators=(",", ":")))

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(page)
    print(f"Wrote {output_path} ({len(page):,} bytes)")


if __name__ == "__main__":
    print(
        "This module is meant to be edited per-earthquake and run directly, "
        "or imported and called via build(...). See the docstring / SKILL.md "
        "step 3-4 for the expected fields.",
        file=sys.stderr,
    )

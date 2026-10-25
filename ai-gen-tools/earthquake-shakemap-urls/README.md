# Earthquake ShakeMap → OSH Facility Search URLs

**This is AI-generated ad hoc tooling, not part of the deployed application.**
It lives in `ai-gen-tools/` rather than `src/` because it isn't built,
tested, or maintained to the same bar as the rest of this repo — it's a
disaster-response utility that Claude generates and updates per-invocation
from a Claude Code skill, checked in here mainly so it's discoverable and
reusable by the team rather than living only on one person's machine. Expect
it to be regenerated/replaced rather than incrementally patched.

## What it does

Turns a USGS ShakeMap's shaking-intensity (MMI — Modified Mercalli
Intensity) contours into OpenSupplyHub `?boundary=...` facility-search URLs,
one per MMI level, for a given earthquake or earthquake sequence (mainshock
+ aftershocks). The goal: find every facility sitting inside a quake's
shaking footprint, for disaster response / impact assessment.

OpenSupplyHub's boundary search takes the shape directly as coordinates
embedded in the URL — there's no file upload. Raw USGS shapes are far too
detailed (thousands of points) and web addresses have a practical length
ceiling, so the raw shape gets buffered (smoothed/padded) and simplified
(thinned) before being encoded. See `SKILL.md` (in the Claude Code skill
this was generated from) for the full reasoning and the several non-obvious
correctness traps in that process — this README doesn't repeat it.

## Two output paths

- **`assets/template_interactive.html` (default)** — a self-contained
  interactive page. Each MMI level has its own buffer/simplify sliders, a
  live redraw, a basemap for orientation, and a live overlay comparison
  against the real USGS contour line for that level, so a shape that looks
  wrong can be fixed by dragging a slider rather than editing code. No
  external network calls at runtime (everything, including the
  [turf.js](https://turfjs.org/) geometry library and a basemap, is
  vendored/embedded) — built to run as a static, shareable HTML file (e.g.
  a Claude Artifact).
- **`assets/template.ipynb`** — a Jupyter notebook covering the same
  pipeline in Python (shapely/geopandas), for users who want raw, editable
  code instead of sliders.

## Building a page for a new earthquake

```bash
cd scripts
python3 -c "
from build_interactive import build
build(
    events={'M7.4 Some Place': 'us6000xxxxxx'},  # USGS event ID(s)
    output_path='../output/some-earthquake.html',
    title='Some Place Boundaries',
    eyebrow='USGS ShakeMap · Some Region',
    h1='M7.4 — Some Place',
    subhead_html='...',
    verify_links_html='...',  # must include the .../shakemap/intensity link
)
"
```

See `build_interactive.py`'s docstring/signature for the full field list.

## Verifying a generated page

```bash
cd scripts
npm install   # only needed once, installs jsdom
node verify_interactive.js ../output/some-earthquake.html
```

Prints `CLEAN` or lists specific problems (broken geometry, a level whose
auto-picked default buffer still doesn't fit under the URL length cap, etc.).

## Files

- `assets/template_interactive.html` — the interactive page template
  (placeholders filled in by `build_interactive.py`)
- `assets/template.ipynb` — the notebook alternative
- `assets/turf.min.js` — vendored [turf.js](https://turfjs.org/) v7 browser
  bundle (MIT licensed), used for all buffer/simplify/union/difference math
  in the interactive page
- `assets/ne_countries_110m.min.geojson` — vendored
  [Natural Earth](https://www.naturalearthdata.com/) 110m admin-0 countries
  (public domain), used as the interactive page's basemap layer; cropped
  per-earthquake by `build_interactive.py`, never embedded in full
- `scripts/build_interactive.py` — builds a page from event ID(s) + header
  content
- `scripts/verify_interactive.js` — headless-DOM (jsdom) smoke test for a
  generated page
- `scripts/verify_notebook.py` — executes and checks a generated notebook
- `scripts/shakemap_boundary.py` — reference copy of the Python geometry
  pipeline used in the notebook, for prototyping tuning changes outside the
  notebook itself
- `scripts/package.json` — the one npm dependency (`jsdom`) needed for
  `verify_interactive.js`

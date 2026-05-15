---
name: figma-frontend-design
description: Create distinctive, production-grade frontend interfaces with high design quality. Use this skill when the user asks to build web components, pages, or applications. Generates creative, polished code that avoids generic AI aesthetics.
---

This skill guides creation of distinctive, production-grade frontend interfaces that avoid generic "AI slop" aesthetics. Implement real working code with exceptional attention to aesthetic details and creative choices.

The user provides frontend requirements: a component, page, application, or interface to build. They may include context about the purpose, audience, or technical constraints.

## Design Thinking

Before coding, understand the context and commit to a BOLD aesthetic direction:
- **Purpose**: What problem does this interface solve? Who uses it?
- **Tone**: Pick an extreme: brutally minimal, maximalist chaos, retro-futuristic, organic/natural, luxury/refined, playful/toy-like, editorial/magazine, brutalist/raw, art deco/geometric, soft/pastel, industrial/utilitarian, etc. There are so many flavors to choose from. Use these for inspiration but design one that is true to the aesthetic direction.
- **Constraints**: Technical requirements (framework, performance, accessibility).
- **Differentiation**: What makes this UNFORGETTABLE? What's the one thing someone will remember?

**CRITICAL**: Choose a clear conceptual direction and execute it with precision. Bold maximalism and refined minimalism both work - the key is intentionality, not intensity.

Then implement working code (HTML/CSS/JS, React, Vue, etc.) that is:
- Production-grade and functional
- Visually striking and memorable
- Cohesive with a clear aesthetic point-of-view
- Meticulously refined in every detail

## Frontend Aesthetics Guidelines

Focus on:
- **Typography**: Choose fonts that are beautiful, unique, and interesting. Avoid generic fonts like Arial and Inter; opt instead for distinctive choices that elevate the frontend's aesthetics; unexpected, characterful font choices. Pair a distinctive display font with a refined body font.
- **Color & Theme**: Commit to a cohesive aesthetic. Use CSS variables for consistency. Dominant colors with sharp accents outperform timid, evenly-distributed palettes.
- **Motion**: Use animations for effects and micro-interactions. Prioritize CSS-only solutions for HTML. Use Motion library for React when available. Focus on high-impact moments: one well-orchestrated page load with staggered reveals (animation-delay) creates more delight than scattered micro-interactions. Use scroll-triggering and hover states that surprise.
- **Spatial Composition**: Unexpected layouts. Asymmetry. Overlap. Diagonal flow. Grid-breaking elements. Generous negative space OR controlled density.
- **Backgrounds & Visual Details**: Create atmosphere and depth rather than defaulting to solid colors. Add contextual effects and textures that match the overall aesthetic. Apply creative forms like gradient meshes, noise textures, geometric patterns, layered transparencies, dramatic shadows, decorative borders, custom cursors, and grain overlays.

NEVER use generic AI-generated aesthetics like overused font families (Inter, Roboto, Arial, system fonts), cliched color schemes (particularly purple gradients on white backgrounds), predictable layouts and component patterns, and cookie-cutter design that lacks context-specific character.

Interpret creatively and make unexpected choices that feel genuinely designed for the context. No design should be the same. Vary between light and dark themes, different fonts, different aesthetics. NEVER converge on common choices (Space Grotesk, for example) across generations.

**IMPORTANT**: Match implementation complexity to the aesthetic vision. Maximalist designs need elaborate code with extensive animations and effects. Minimalist or refined designs need restraint, precision, and careful attention to spacing, typography, and subtle details. Elegance comes from executing the vision well.

Remember: AI agent is capable of extraordinary creative work. Don't hold back, show what can truly be created when thinking outside the box and committing fully to a distinctive vision.

---

## Default Figma Frame Sizes

**Always create both a desktop and a mobile frame for every new design**, even if the brief only mentions one. Place them side by side on the canvas — desktop at x=0, mobile at x=desktop_width+200.

| Frame | Size | Prototyping Device | Figma frame name |
|---|---|---|---|
| Desktop | **1728 × 1117 px** (auto-height) | MacBook Pro 16 | `Desktop/{PageName}` |
| Mobile | **390 × 844 px** (auto-height) | iPhone 14 | `Mobile/{PageName}` |

Both frames use VERTICAL auto-layout: `layoutMode = 'VERTICAL'`, `primaryAxisSizingMode = 'AUTO'`, `counterAxisSizingMode = 'FIXED'`, `itemSpacing = 0`, no padding.

---

## OSH (Open Supply Hub) Brand System

When designing for the Open Supply Hub product, apply the following brand and design system exactly. This is extracted from the live site (opensupplyhub.org) and validated design work.

### Brand Colors

| Token | Hex | Usage |
|---|---|---|
| `--osh-purple` | `#8428FA` | Nav active states, CTAs, interactive links, map pins (verified), section label accents, borders on active nodes, button borders |
| `--osh-navy` | `#0D1128` | Footer background, all heavy headings, wordmark, primary dark text |
| `--osh-yellow` | `#FCCF3F` | Pending/claim badge icons, map markers (unverified), status badge borders |
| `--osh-pink` | `#FFA6D0` | Footer geometric decorative accents |
| `--osh-lavender-100` | `#E6D4FE` | Card/callout backgrounds (e.g. OS ID block, barcode block, verified chip bg) |
| `--osh-lavender-200` | `#CEA9FD` | Borders on highlighted info blocks, timeline connector lines |
| `--osh-off-white` | `#F9F7F7` | Overall page surface, section backgrounds alternating with white |
| `--osh-white` | `#FFFFFF` | Card surfaces, header background |
| `--osh-text` | `#0D1128` | Primary headings |
| `--osh-label` | `#757575` | Muted metadata labels ("Location Name", "Address", breadcrumb separators) |
| `--osh-orange-light` | `#FFF3E0` | Unverified/crowdsourced chip background |
| `--osh-orange-text` | `#E65100` | Unverified/crowdsourced chip text |

### Typography

- **Font family**: `'Darker Grotesque', sans-serif` — available in Figma and Google Fonts
- **Heading weight**: Black (900) for all major headings
- **Body/UI weight**: Bold (700) for nav, buttons, labels; SemiBold (600) for section labels; Regular (400) for body copy
- **Letter spacing**: Section labels (e.g. "SUPPLY CHAIN JOURNEY") use `10%` letter spacing, uppercase, 10–11px, in `#8428FA`
- **Section headings**: 36px Black, `#0D1128`
- **Product name / hero heading**: 44px Black, `#0D1128`, line height 105%

### Tone

Editorial precision, civic-tech / data transparency. Not consumer glossy. Every layout decision should feel intentional. Strong typographic hierarchy, generous whitespace, `#8428FA` purple as the dominant interactive color, `#FCCF3F` yellow for action/alert states, `#0D1128` navy as the heavy structural color.

---

## OSH Figma Design — Validated Patterns & Corrections

The following patterns were validated (and some corrected) during actual Figma production work. Apply these exactly when building OSH screens in Figma via the Plugin API.

### Layout: Auto-Layout Heading Rows

**Problem**: A horizontal heading row containing a text heading + spacer + button, when inside a VERTICAL auto-layout parent, will collapse to HUG width (matching only the text width) and clip the button.

**Fix — always apply both:**
```js
headingRow.layoutSizingHorizontal = 'FILL'; // expand to parent width
headingRow.clipsContent = false;             // never clip children
```

Also ensure the heading text node uses `textAutoResize = 'WIDTH_AND_HEIGHT'` (requires font to be loaded first).

### Timeline Connectors: Arrow Direction

**Problem**: Using `figma.createPolygon()` rotated -90° for a right-pointing arrowhead produces inconsistent positioning — the visual tip does not land at the expected x/y coordinate.

**Fix — always use a Vector node with an explicit path:**
```js
const arrow = figma.createVector();
arrow.name = 'ConnectorArrow';
arrow.vectorPaths = [{
  windingRule: 'NONZERO',
  data: `M 0 0 L ${ARROW_W} ${ARROW_H / 2} L 0 ${ARROW_H} Z`
}];
arrow.fills = [solid('#8428FA')];
arrow.strokes = [];
// Position: flush with right edge of connector frame, vertically centered
arrow.x = CONN_W - ARROW_W;
arrow.y = centerY - ARROW_H / 2;
```

The connector line should end exactly at `x = CONN_W - ARROW_W` so the line tip and arrow base are flush. Connector frames must use `layoutMode = 'NONE'` (absolute positioning) for line and arrow to be placed independently.

### Map Section: Real Satellite Imagery

**Do not use placeholder rectangles for maps.** Use real ESRI World Imagery satellite tiles.

**Tile download recipe (Python + Pillow):**
```python
import urllib.request, math, io
from PIL import Image

zoom = 3
tiles_x = [3, 4, 5, 6, 7]   # lon: -45° to 180°
tiles_y = [2, 3, 4]          # covers 66.5°N to -41°S (Mercator)
tile_size = 256
headers = {'User-Agent': 'Mozilla/5.0 (compatible)'}

mosaic = Image.new('RGB', (len(tiles_x)*256, len(tiles_y)*256))
for row_i, y in enumerate(tiles_y):
    for col_i, x in enumerate(tiles_x):
        url = f'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{zoom}/{y}/{x}'
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            tile = Image.open(io.BytesIO(resp.read())).convert('RGB')
            mosaic.paste(tile, (col_i*256, row_i*256))

# Crop to show ~55°N to ~-8°S (supply chain geography: EU + Asia)
# Mercator: tile y=2 starts at global y=512; top of crop at y_global=648 (55°N)
top_local = 648 - 512   # = 136
cropped = mosaic.crop((0, top_local, 1280, top_local + 420))
cropped.save('/tmp/satellite_map.jpg', 'JPEG', quality=92)
```

**Pin positioning — use Mercator projection, not linear lat:**
```python
def lat_to_y_global(lat_deg):
    lat_rad = math.radians(lat_deg)
    n, tile = 8, 256
    return (1 - math.log(math.tan(lat_rad) + 1/math.cos(lat_rad)) / math.pi) * n * tile / 2

lat_top_global = lat_to_y_global(55.0)   # 648
lat_bot_global = lat_to_y_global(-8.0)   # 1070
lon_start, lon_range = -45.0, 225.0

def pin_x(lon): return (lon - lon_start) / lon_range * 1280
def pin_y(lat): return (lat_to_y_global(lat) - lat_top_global) / (lat_bot_global - lat_top_global) * 420
```

**Known pin positions (1280×420 desktop map):**

| Facility | Lon | Lat | x | y | Color |
|---|---|---|---|---|---|
| Leipzig, DE | 12.3 | 51.3 | 326 | 35 | `#8428FA` |
| Xinjiang, CN | 83.0 | 41.0 | 728 | 120 | `#FCCF3F` |
| Shandong, CN | 118.0 | 37.0 | 927 | 149 | `#8428FA` |
| Dhaka, BD | 90.4 | 23.7 | 770 | 237 | `#FCCF3F` |
| HCMC, VN | 106.7 | 10.8 | 863 | 314 | `#8428FA` |
| Jakarta, ID | 106.8 | -6.2 | 864 | 400 | `#8428FA` |

Upload satellite image to Figma using `upload_assets` with the map placeholder node ID, then use `use_figma` to remove old children and re-add: glow ellipse (30% opacity), pin ellipse (white stroke, drop shadow), dark tooltip label above pin, and a legend frame (white 92% opacity, rounded, drop shadow).

### Real Logo: Rendering from SVG Source

**Do not use placeholder shapes for the OSH logo.** Render the real SVG from the codebase.

**Source files:**
- Header logo (dark): `src/react/src/components/Navbar/Logo.jsx` — viewBox `0 0 972.96 364.15`, fill `#0D1128`
- Footer logo (white): `src/react/src/components/Footer/FooterLogo.jsx` — viewBox `0 0 86 32`, fill `#fff`

**Rendering recipe:**
```bash
# Install rsvg-convert (one-time):
brew install librsvg

# Render at target height (preserves aspect ratio):
rsvg-convert -h 60 logo_dark.svg -o logo_header_dark.png   # → 161×60
rsvg-convert -h 60 logo_white.svg -o logo_header_white.png # → 161×60
```

**Uploading and applying to Figma:**
1. Create a `figma.createFrame()` of the target size (e.g. 113×42 for desktop header)
2. Insert it into the auto-layout parent at position 0 with `FIXED` sizing
3. Upload the PNG via `upload_assets` (without nodeId) to get the `imageHash`
4. Apply via `use_figma`: `frame.fills = [{ type: 'IMAGE', imageHash, scaleMode: 'FIT' }]`
5. Delete the auto-created temp node from the upload

**Target sizes:**
| Location | Width | Height | Logo variant |
|---|---|---|---|
| Desktop header | 113 | 42 | Dark (`#0D1128`) |
| Desktop footer | 97 | 36 | White (`#FFFFFF`) |
| Mobile header | 81 | 30 | Dark (`#0D1128`) |
| Mobile footer | 75 | 28 | White (`#FFFFFF`) |

Logo aspect ratio: `161 / 60 = 2.683`

### Figma Variables: Scope Conflict

When creating color variables, do NOT combine `ALL_FILLS` with other fill-specific scopes — Figma will throw:
> `"If ALL_FILLS is set, other fill scopes cannot be set"`

Use either `['ALL_SCOPES']` (simplest) or a single specific scope list without `ALL_FILLS` mixed with others.

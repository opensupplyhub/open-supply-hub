---
name: figma-design-to-page
description: Convert a Figma design URL into a new production-ready React page in the Open Supply Hub app. Use when the user shares a Figma link and asks to build or implement it as a new page in the react app.
---

# Figma Design → New Page (OSH)

## Required Workflow

**Follow every step in order. Do not skip any.**

### Step 1 — Fetch Design Context

Parse the Figma URL:
- File key: segment after `/design/`
- Node ID: `node-id` query param value

Run in parallel:
```
get_design_context(fileKey, nodeId)   // full layout + tokens
get_screenshot(fileKey, nodeId)       // keep as visual reference
```

If the response is too large, call `get_metadata` first, then fetch each major section separately.

### Step 2 — Explore the Codebase

Before writing any code, explore in parallel:
- **MUI version**: check `src/react/package.json` — the app uses `@material-ui/core` v3, NOT `@mui/material`
- **Routing**: `src/react/src/Routes.jsx` + route constants in `src/react/src/util/constants.jsx`
- **Colors/tokens**: `src/react/src/util/COLOURS.js` and `OARColor` / `OARSecondaryColor` from `constants.jsx`
- **Existing page pattern**: read 1–2 existing page components from `src/react/src/components/` for naming and structure conventions

### Step 3 — Implement the Page

**File locations:**
1. Add route constant to `src/react/src/util/constants.jsx`
2. Create `src/react/src/components/{PageName}.jsx`
3. Add import + `<Route>` to `src/react/src/Routes.jsx` — place it **before** the `mainRoute`/Facilities catch-alls

**Component template:**
```jsx
import React from 'react';
import { withStyles } from '@material-ui/core/styles';
// only import MUI components you actually use

const styles = { /* JSS styles */ };

function MyPage({ classes }) { return (...); }

export default withStyles(styles)(MyPage);
```

### Step 4 — Browser Review

After implementing, open the page in the browser and check every section. Fix all visual issues before calling it done. See the validation checklist below.

---

## Rules — Must Apply Before Calling It Done

These rules were learned from real corrections. Apply ALL of them proactively.

### MUI v3 API

- Use `withStyles` from `@material-ui/core/styles` — **not** `makeStyles` (added in v4)
- No `Breadcrumbs` component in v3 — build a custom breadcrumb row with spans
- `Chip` renders a `<div>` with a label — style via `className`
- `Button` has `textTransform: uppercase` by default — override in styles with `textTransform: 'none'`

### Never Use Typography Heading Variants

`<Typography variant="h1">` and `variant="h2"` apply MUI defaults of ~96px and ~56px, which override `withStyles` font sizes.

**Always use:**
```jsx
<div className={classes.sectionTitle} role="heading" aria-level="2">
  Heading text
</div>
```

Add `margin: 0` to the styles to remove browser `<h1>`/`<h2>` default margins if you ever use native heading elements.

### No Unused Imports

The linter enforces `no-unused-vars` and **fails the build**. Only import what is actually rendered. Commonly unused: `Paper`, `Grid`, `COLOURS`, `Typography`.

### No Array Index Keys

The linter enforces `react/no-array-index-key` and **fails the build**. Add a stable `id` field to every static data array and use it as the `key`:
```jsx
// ✅ correct
const BARS = [{ id: 'b01', ... }, { id: 'b02', ... }];
{BARS.map(bar => <div key={bar.id} />)}

// ❌ fails build
{BARS.map((bar, i) => <div key={i} />)}
```

### Responsive Layout

The design is built for 1440px but the app is viewed at real viewport sizes. **Always add responsive breakpoints** in JSS using `@media`:

```js
heroInner: {
    padding: '48px 80px',
    '@media (max-width: 1100px)': { padding: '40px 32px' },
    '@media (max-width: 700px)':  { padding: '32px 16px' },
},
heroColumns: {
    display: 'flex',
    gap: '48px',
    '@media (max-width: 900px)': { flexDirection: 'column', gap: '32px' },
},
```

Add `minWidth: 0` to every `flex: 1` column so it can shrink below its content width.

### No overflow: hidden on Outer Sections

Do not add `overflow: 'hidden'` to hero sections or full-width section wrappers — it clips the right column at narrow viewports.

### flexShrink: 0 Causes Horizontal Overflow

`flexShrink: 0` on a row child with long text content will extend past the viewport. Use `flex: 1, minWidth: 0` for expanding info containers:
```js
// ✅
provenanceLeft: { flex: 1, minWidth: 0, display: 'flex', gap: '12px' }

// ❌ overflows viewport
provenanceLeft: { flexShrink: 0, display: 'flex', gap: '12px' }
```

### Text Wrapping

Remove `whiteSpace: 'nowrap'` from any element that should wrap on narrow screens (facility names, addresses, long metadata strings). Only keep `whiteSpace: 'nowrap'` on short single-word labels or badges where wrapping is never correct.

---

## Validation Checklist

Run through every section in the browser before finishing.

```
- [ ] Page compiles with zero errors (no unused imports, no index keys)
- [ ] Hero: title renders at correct font size (not MUI h1 96px default)
- [ ] Hero: barcode / right-column card is fully visible (not clipped)
- [ ] Timeline: nodes and connectors are horizontally scrollable at narrow widths
- [ ] Facility cards: names wrap correctly, "View Facility" button is not overlapping
- [ ] Map: image and pins render; legend overlay is visible
- [ ] Data provenance: detail text wraps and is not cut off at viewport edge
- [ ] All sections have correct background colors (alternating white / #F9F7F7)
- [ ] No horizontal scroll bar on the page at any tested viewport width
```

---

## OSH Color Reference

| Token in COLOURS.js | Hex | Usage |
|---|---|---|
| `COLOURS.PURPLE` / `OARColor` | `#8428FA` | Primary interactive, links, active borders |
| `COLOURS.NEAR_BLACK` | `#0D1128` | All headings and heavy text |
| `#757575` | — | Muted labels (MID_GREY) |
| `COLOURS.LIGHT_GREY` | `#F9F7F7` | Alternating section background |
| `#E6D4FE` | — | Chip / badge backgrounds (light purple) |
| `#CEA9FD` | — | Highlighted info block borders |
| `COLOURS.NAVIGATION` | `#FCCF3F` | Pending/alert badge color |

Font: `'Darker Grotesque', sans-serif` — imported via `typeface-darker-grotesque` in `App.jsx`.

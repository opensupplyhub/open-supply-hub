# Typography Guide

How to use typography across the application: which shared styles to use, how to combine them with MUI `Typography`, and when to use each.

---

## 1. Source of truth

- **File:** `src/react/src/util/typographyStyles.js`
- **Usage:** Call `getTypographyStyles(theme)` in your component's `withStyles` (or `makeStyles`) and spread the returned keys into your class objects; then pass those classes to MUI `Typography` via `className={classes.xyz}`.
- **Rule:** Prefer these tokens over hardcoding font sizes/weights so headings, labels, body text, and links stay consistent.
- **Body text size:** Use `1rem` for body and paragraph text (section description, bodyText, inline highlight). In this app the root font size is the browser default (typically 16px), so 1rem resolves accordingly.
- **MUI v3 Typography variants:** Use `component` for semantics (e.g. `component="h1"`) and `variant` for MUI’s styling. Valid variants are: `"display4"`, `"display3"`, `"display2"`, `"display1"`, `"headline"`, `"title"`, `"subheading"`, `"body2"`, `"body1"`, `"caption"`, `"button"`, `"srOnly"`, `"inherit"`. Do not use `variant="h1"` / `"h2"` / `"h3"` (they are not supported in MUI v3). Use `variant="headline"` for page title, `variant="title"` for major/section headings, `variant="subheading"` for sub-sections.

---

## 2. Semantic roles and which style to use

| Role | When to use | Style key | Typical MUI usage |
|------|-------------|-----------|-------------------|
| **Page title** | Main title of a page (e.g. facility/location name) | (custom from `formLabelTight`) | `<Typography component="h1" variant="headline" className={classes.title} />` |
| **Major section** | Big section blocks (e.g. claim intro) | (custom as needed) | `component="h2"`, `variant="title"` |
| **Section title** | Subsections ("Understanding Data Sources", "Partner Data", etc.) | `sectionTitle` | `component="h3"`, `variant="title"`, `className` with `...typography.sectionTitle` |
| **Field / UI label** | Form labels, bold labels ("OS ID:", "CLAIMED PROFILE", "Claimed", "Crowdsourced") | `formLabel` or `formLabelTight` | `component="span"` or `"label"`, `variant="body1"`, `className` with `...typography.formLabelTight` |
| **Body / paragraph** | Normal paragraphs, descriptions, "Show more" labels | `bodyText` | `component="p"` or `"span"`, `variant="body1"`, `className` with `...typography.bodyText` |
| **Section description** | Intro or explanatory block under a section | `sectionDescription` | `component="p"`, `variant="body1"`, `className` with `...typography.sectionDescription` |
| **Inline highlight** | Short emphasized bits (name, date, ID value) inline in text | `inlineHighlight` | `component="span"`, `className` with `...typography.inlineHighlight` |

---

## 3. Style attributes (from `typographyStyles.js`)

- **formLabel / formLabelRoot / formLabelTight**  
  Base: `fontSize: '21px'`, `fontWeight: 600`.  
  `formLabel` adds `margin: '24px 0 8px 0'`; `formLabelRoot` uses `marginTop: 0`, `marginBottom: '8px'`; `formLabelTight` has no extra margin.  
  Use for field labels and strong short labels.

- **sectionTitle**  
  `fontSize: '24px'`, `fontWeight: theme.typography.fontWeightSemiBold`, `marginTop: '25px'`.  
  Use for h3-level section titles.

- **sectionDescription**  
  `fontSize: '1rem'`, `marginBottom: '10px'`.
  Use for the first paragraph or intro under a section.

- **bodyText**  
  `fontSize: '1rem'`, `color: theme.palette.text.secondary`.
  Use for regular body and secondary text.

- **inlineHighlight**  
  `fontSize: '1rem'`, `fontWeight: 500`, `color: theme.palette.text.primary`, `display: 'inline'`.
  Use for emphasized inline pieces (e.g. facility name, date, OS ID value).

---

## 4. Headings

- **h1 – Page title**  
  One per page (e.g. facility/location name).  
  Example: `component="h1"`, `variant="headline"`, `className` from styles that extend `formLabelTight` (e.g. 28px, 700 for prominence).

- **h2 – Major section**  
  Top-level sections (e.g. claim intro).  
  `component="h2"`, `variant="title"`, plus custom class if needed.

- **h3 – Section title**  
  Subsections ("Understanding Data Sources", "Partner Data", "Interactive map", etc.).  
  `component="h3"`, `variant="title"`, `className` with `...typography.sectionTitle` (and margin overrides as needed, e.g. `marginTop: 0`).

- **h4 / h5 / h6**  
  Use sparingly for sub-subsections (e.g. ClaimFlag uses `h4` for "CLAIMED PROFILE").  
  Prefer a class that extends `formLabelTight` or `sectionTitle` so sizing stays consistent. Use MUI v3 variants such as `"title"` or `"subheading"` (not `"h4"`/`"h5"`/`"h6"`).

---

## 5. Regular text

- **Paragraphs:**  
  `component="p"`, `variant="body1"`, and a class that includes `...typography.bodyText` (and optionally `...typography.sectionDescription` for intro blocks).  
  Body text uses `fontSize: '1rem'`. Override `fontSize` or `marginBottom` only when needed.

- **Inline text / labels:**  
  `component="span"`, `variant="body1"`, and either `formLabelTight` (labels) or `bodyText` (secondary inline).

---

## 6. Links

- **Color:** `theme.palette.primary.main`.
- **Implementation:**  
  Use `<a href="..." className={classes.link}>` or `<Link to="..." className={classes.link}>` with a style like `link: { color: theme.palette.primary.main }`.  
  For "Learn more →" in tooltips, inline `style={{ color: 'white' }}` is used for contrast on dark tooltip background; elsewhere use the theme primary color.
- **Optional:** Add `textDecoration: 'none'` and `'&:hover': { textDecoration: 'underline' }` for inline links (e.g. in DataSourcesInfo `learnMoreLink`).

---

## 7. Usage pattern

1. In the component's `styles.js`:  
   `import { getTypographyStyles } from '../../path/to/typographyStyles';`  
   then `const typography = getTypographyStyles(theme);` and use `...typography.sectionTitle`, etc., in your class objects.

2. In the JSX:  
   Use MUI `Typography` with both:
   - **Semantic props:** `component` (e.g. `component="h3"`) for the HTML element and `variant` for MUI v3 styling (e.g. `variant="title"` or `variant="subheading"` — use only valid MUI v3 variants, not `"h1"`/`"h2"`/`"h3"`).
   - **Visual style:** `className={classes.yourClass}` where `yourClass` spreads the right typography token and any local overrides.

3. Keep **one** clear hierarchy per page: one h1, then h2/h3 as needed; use the table in §2 to pick the right style key and component/variant.

---

## 8. Quick reference

| Use case | component | variant | Typography style key |
|----------|-----------|--------|----------------------|
| Page title (e.g. facility name) | h1 | headline | formLabelTight (custom size/weight) |
| Section title | h3 | title | sectionTitle |
| Field / subsection label | span | body1 | formLabelTight |
| Paragraph / body | p | body1 | bodyText or sectionDescription |
| Inline emphasis (name, ID, date) | span | — | inlineHighlight |
| Links | a or Link | — | color: theme.palette.primary.main |

---

## 9. Container styles (commonStyles)

- **File:** `src/react/src/components/ProductionLocation/commonStyles.js`
- **Purpose:** Shared base styles for section containers (e.g. cards, content blocks) so background and shadow stay consistent across the Production Location UI.

### What it provides

`commonStyles(theme)` returns an object with a `container` key:

- **container:** `backgroundColor: theme.palette.background.white`, `boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)'`

### How to use it

Spread `commonStyles(theme).container` into your own container class and add any overrides (margin, padding, etc.). This keeps the same background and shadow while letting each component set its own spacing.

**Import in your styles file:**

```js
import commonStyles from '../../commonStyles';  // adjust path to your component
```

**Example – extend and override:**

```js
container: Object.freeze({
    ...commonStyles(theme).container,
    marginBottom: spacing * 3,
    padding: '20px 20px 20px 36px',
}),
```

Here the container gets the shared `backgroundColor` and `boxShadow` from `commonStyles`, plus component-specific `marginBottom` and `padding`. Use this pattern for any Production Location section that should look like a card (e.g. LocationTitle, DataSourcesInfo).

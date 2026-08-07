---
name: os-hub-design
description: Use this skill to generate well-branded interfaces and assets for Open Supply Hub (OS Hub). Contains design guidelines, colors, type, voice rules, CSS tokens, component recipes, slide layout patterns, and inline SVG brand assets.
user-invocable: true
---

# Open Supply Hub Design System — single-file edition

This is a self-contained Markdown export of the OS Hub design system. Everything textual is embedded below: brand guide, voice rules, CSS tokens, React component sources, slide layout HTML, and SVG assets (inline, ready to save to disk). Raster assets (PNG mosaics/shapes/icons) and font binaries could NOT be embedded — see "What is not in this file" at the end.


---

# 1. DESIGN GUIDE (readme.md)

# Open Supply Hub Design System

**Open Supply Hub (OS Hub)** — opensupplyhub.org — is a US-based 501(c)(3) non-profit powering the transition to safe and sustainable supply chains with "the world's most complete, open and accessible map of global production." The platform assigns a universal **OS ID** to every production location, lets anyone search and contribute data, and serves brands & retailers, civil society, industry organizations, and manufacturing groups. Key stats (2026, verify before use): more than 2.5 million production locations, 4,500+ data contributors, 3,700+ claimed profiles.

Products/surfaces represented in the sources: **presentation decks** (intro/sales deck + event deck) plus organization-wide brand and comms standards. No product-app codebase or Figma was provided, so this system is built for branded collateral — decks, one-pagers, mocks — not a UI recreation of the platform.

## Sources
- `uploads/[MAKE A COPY] May 2026 - Intro Deck .pptx` — 102-slide master intro deck (copied to `uploads/intro-deck.pptx`)
- `uploads/LUPC Responsible Procurement Event_July 2026.pptx` — 22-slide event deck (copied to `uploads/lupc-deck.pptx`)
- `uploads/Brand Colors.png.pdf` — official palette with HEX/CMYK/RGB/Pantone
- `uploads/OS Hub Brand + Style Guide (dragged)*.pdf` — 9 pages of the Brand Guidelines (Spring 2022): cover, icon, wordmark, logo rules, typography, color, color+text, shapes, shape compositions (copied to `uploads/sg-1..9.pdf`; page renders in `extracted/styleguide/`)
- `uploads/OSHub_ExternalComms_StyleGuide_FINAL 2026 (1).md` — External Communications Style Guide (June 2026): naming, messaging framework, voice & tone, AP style rules, audience profiles, channel guidelines. **Read it before writing any OS Hub copy.**
- Extracted deck text: `extracted/intro-text.md`, `extracted/lupc-text.md`
- Local folder `2026 Q1 OS Hub Board of Directors meeting_April 2026/` — 75 slide screenshots of the Q1 2026 board deck (copies in `extracted/board-deck/`); source of the section-rail, topic-bar, band-header, key-notes, callout-box, motion, and big-number slide patterns

## CONTENT FUNDAMENTALS

**Name.** Full name **Open Supply Hub**; short form **OS Hub** only after the full name has appeared once. NEVER: OSH, OSHub, the hub, OS-Hub. Say "the OS Hub platform" / "the platform" thereafter. Describe as "a global open data platform" or "a non-profit platform." ALL CAPS only in logo/wordmark contexts; title case in running text.

**Tagline:** *Data that opens doors to safe and sustainable supply chains.* Core brand verbs, always in this order: **Share | Discover | Collaborate** (Share = contribute data; Discover = find connections, gaps, opportunities; Collaborate = act by partnering). Approved one-liner: "Open Supply Hub is powering the transition to safe and sustainable supply chains with the world's most complete, open and accessible map of global production." Full boilerplates live in the comms style guide.

**Voice** (comms guide, June 2026): concise, clear, empathetic. Precise over vague ("facility-level data across more than 2.5 million production locations," never "comprehensive supply chain intelligence"). Outcome-led, not feature-led. Confident without being promotional — no unearned superlatives ("industry-leading," "groundbreaking"). Mission-anchored without being preachy. Honest about coverage gaps.

**The brand has no emotions:** never "we're excited/thrilled/proud" in brand voice. No white-savior framing — OS Hub does not "help" or "empower" communities; it builds infrastructure that enables action. No urgency theater ("you need this before CSDDD hits").

**Structure ("OS Hub Piano"):** 01 Inspire (the possibility) → 02 Explore (cases, real impact) → 03 Engage (how it works, how to get involved). Never lead with features.

**Grammar:** AP Style baseline, American English. **Sentence case for headings** (2026 standard — existing decks use Title Case; new content should use sentence case; press-release headlines are the title-case exception). Always the Oxford comma. **"non-profit" hyphenated.** Figures for 10 and above; % symbol always; spell out acronyms on first use. Em dashes spaced — like this — and used sparingly. Active voice; no hedging ("helps," not "may potentially help"). Descriptive link text, never "click here." Round platform stats ("more than 2.5 million production locations") and verify before publishing.

**Emoji:** none in brand contexts. LinkedIn allows 1–2 max, never in the opening line, never in formal announcements, no skin-tone modifiers.

**Deck patterns:**
- Short declarative statement slides: "Every product comes from a supply chain."
- Emphatic mid-sentence bolding of key phrases.
- Uppercase eyebrows/kickers for wayfinding: "CASE STUDY", "FIND OUT MORE", "FEATURES: …".
- Big rounded stat callouts: "2,500,000+ / Production locations listed".
- Case studies: eyebrow → benefit-led headline → narrative → pull quote → org boilerplate → "FIND OUT MORE".

## VISUAL FOUNDATIONS

**Color.** "Bright and bold… cheerful and inviting, without becoming chaotic or childish." Cream `#F9F7F7` is the **default background**; navy/black `#0D1128` the primary text color; purple `#8428FA` the lead accent (CTAs, highlights). Red `#FF2727` is accent-only, very sparing in text. **Pairing rules:** cream bg → black/purple/(red) text; yellow/pink/green bg → black text; purple/black bg → cream text; red bg → cream text, very sparingly. Accents at full saturation as solid shapes/panels — never gradients. Light-green tint `#AAE2B3` in map/illustration fills.

**Logo.** The icon is a geometric "puzzle pieces" abstraction of a **hub-and-spoke** form — square aspect, diagonal axes and rotational symmetry (motion), aperture/target associations (opening, focusing, convergence, precision). Wordmark: "OPEN SUPPLY HUB" in Darker Grotesque, three lines, ALL CAPS, anchored by the icon. **The icon may stand alone; the wordmark may never appear without the icon.** Clear space: 40% of icon height between the logo and any other element. Don't stretch, compress, or tilt; never set the wordmark in lowercase or a light weight.

**Type.** `Darker Grotesque` is the brand typeface — free Google font, seven weights Light→Black, "balances legibility with personality" (swooping legs on R, deep vertexes in M/N, angular ascenders/descenders on g/f/y). Guide specimen: headings Black at **92% line-height**, 0 tracking; body Medium at **130% line-height**. Arial is the office-tools substitute. The 2026 decks additionally use `DM Sans` for small body text (kept as the default body face here). Known bug: Darker Grotesque quotation marks render backwards on some platforms — check and mirror manually.

**Shapes.** Brand metaphor: shapes are **pieces of data** — "opening data brings pieces together to create complete, vibrant, impactful stories." Vocabulary: circle, triangle, square, quarter-round, arch/semicircle, starburst, checkerboard. **Composition rules:** arrange on a square grid with a base of 6, 8, or 12 squares; never place the same color in two adjacent blocks; balance visually heavy shapes (large solid square) with lighter ones (starburst, checkerboard).

**Backgrounds.** Flat cream or off-black, decorated with the shape-mosaic motif hugging a corner or edge (see `assets/backgrounds/`). Full-bleed mosaic panels for title slides; corner clusters or confetti strips for content slides; yellow banners with dark starbursts for section headers.

**Illustration.** Two families: (1) flat geometric shapes/pictograms (purple person, arches, world map); (2) mono-weight line drawings in a single accent color (yellow car, red sneaker, green phone, purple laptop) plus dashed purple journey paths and hand-drawn arrows & speech bubbles. Line icons for sectors are off-black thin-line on off-white circles.

**Shape language (UI).** Square corners dominate; pills for buttons/tags; ~16px radius for cards. **No drop shadows** — separation via solid color blocks and thin off-black keylines. No blur/transparency effects.

**Motion.** Sources are static; no animation system defined. Keep any motion to simple fades/slides.

**Imagery.** Sparse photography: team headshots and occasional documentary photos. Illustration-first brand. Formal imagery guidance is "[TO DEVELOP]" per the comms guide — treat worker/facility photography with care.

## ICONOGRAPHY

- **No icon font.** Icons in decks are PNG/SVG images: thin off-black line icons (sector icons, stakeholder icons) on off-white circular chips — copied to `assets/icons/`.
- Hand-drawn speech bubbles and arrows are used as annotation devices (`assets/illustrations/`).
- The **star/asterisk icon** (hub-and-spoke pinwheel) doubles as a decorative element and may stand alone.
- No emoji, no unicode-glyph icons.
- For icons beyond the copied set, the closest CDN match is **Lucide at 1.25–1.5px stroke** (flagged substitution — confirm with brand team).

## Fonts

Brand typeface "Darker Grotesque" (and deck body face "DM Sans") fetched from Google Fonts (variable, latin subset) into `assets/fonts/` — declared in `tokens/fonts.css`. Arial is the sanctioned substitute in everyday tools. The decks also reference an "OSH Darker Grotesque" custom cut we do not have — supply it if it differs.

## Index

- `styles.css` — global entry; imports `tokens/{colors,typography,spacing,fonts,base}.css`
- `assets/logos/` — full logo (dark/white, SVG+PNG), star icon (dark/white)
- `assets/backgrounds/` — mosaic-dark/light, corner-cluster, globe-community, yellow banner, confetti strip
- `assets/shapes/` — solid geometry: circles, triangles, semicircles, petals, burst, checkerboard, fan-lines, person, network node
- `assets/illustrations/` — line art: car, sneaker, phone, meal, laptop, dashed paths, arrows, speech bubbles, world map
- `assets/icons/` — 9 sector line icons + 8 misc line icons
- `assets/fonts/` — Darker Grotesque + DM Sans variable woff2
- `components/core/` — Button, Tag, Eyebrow, Stat, Card, SpeechBubble (see prompt.md files)
- `slides/` — 15 sample slide layouts recreated from the decks: Title (dark + light), Statement, Section Rail, Pillars, Stats, Case Study, Section Divider, Topic Bar, Band Header, Key Notes, Callout Boxes, Motion, Big Number Flow, Contact
- `templates/osh-deck/` — "OS Hub Deck" starting-point template: 13-slide branded deck shell
- `guidelines/` — foundation specimen cards for the Design System tab
- `uploads/OSHub_ExternalComms_StyleGuide_FINAL 2026 (1).md` — full comms style guide (voice, channels, audiences)
- `extracted/` — raw extraction working files (deck text, deck media, brand-guide page renders)

## Intentional additions

No component source (Figma/codebase) was provided, so a small set of deck/collateral primitives was authored from patterns observed in the decks: Button (deck CTA "GET PRICING"), Tag, Eyebrow, Stat, Card, SpeechBubble. Nothing else invented.


---

# 2. CSS TOKENS

Save these as-is; `styles.css` imports them.

## styles.css

```css
@import "tokens/colors.css";
@import "tokens/typography.css";
@import "tokens/spacing.css";
@import "tokens/fonts.css";
@import "tokens/base.css";
```

## tokens/colors.css

```css
/* Open Supply Hub — color tokens
   Source: OS Hub Brand Guidelines (Spring 2022) + Brand Colors PDF
   + External Comms Style Guide (June 2026).
   Pairing rules: cream is the default background (black, purple, or — sparingly —
   red text). Yellow/pink/green backgrounds take black text. Purple and black
   backgrounds take cream/white text. Red may back cream text, very sparingly. */

:root {
  /* Base palette */
  --osh-off-black: #0D1128;   /* "Navy/Black" — primary text, dark backgrounds */
  --osh-purple: #8428FA;      /* accents, CTAs, highlights, dark backgrounds */
  --osh-purple-deep: #862CF9; /* deck variant, used interchangeably with purple */
  --osh-red: #FF2727;         /* accent only — very sparing in text contexts */
  --osh-pink: #FFA6D0;        /* light backgrounds, audience headers, accents */
  --osh-green: #62CC74;       /* positive indicators, accent backgrounds */
  --osh-green-tint: #AAE2B3;  /* light green tint (map fills, soft panels) */
  --osh-yellow: #FCCF3F;      /* warm accent backgrounds, infographic elements */
  --osh-off-white: #F9F7F7;   /* "Cream/White" — default background */
  --osh-white: #FFFFFF;

  /* Semantic aliases */
  --text-body: var(--osh-off-black);
  --text-heading: var(--osh-off-black);
  --text-inverse: var(--osh-off-white);
  --text-muted: rgba(13, 17, 40, 0.65);

  --surface-page: var(--osh-off-white);
  --surface-page-dark: var(--osh-off-black);
  --surface-card: var(--osh-white);
  --surface-highlight: var(--osh-yellow);

  --accent-primary: var(--osh-purple);
  --accent-positive: var(--osh-green);
  --accent-alert: var(--osh-red);
  --accent-soft: var(--osh-pink);

  --border-strong: var(--osh-off-black);
  --link-color: var(--osh-purple);
  --link-hover-color: var(--osh-off-black);
}
```

## tokens/typography.css

```css
/* Open Supply Hub — typography tokens
   Brand guide (Spring 2022): Darker Grotesque is THE brand typeface (7 weights,
   Light→Black, free Google font) — suitable for both large headlines AND body copy.
   Specimen: headings Black 92% line-height / 0 tracking; body Medium 130% line-height.
   Arial is the approved substitute in everyday tools (Google Docs, HubSpot).
   The 2026 decks additionally use "DM Sans" for small body text — kept here as
   the default body face for on-screen legibility at small sizes. */

:root {
  --font-display: "Darker Grotesque", "Arial Narrow", sans-serif;
  --font-body: "DM Sans", "Helvetica Neue", Arial, sans-serif;

  /* Weights (both families are variable 300–900 / 100–1000) */
  --weight-display-bold: 700;
  --weight-display-black: 800;
  --weight-body: 400;
  --weight-body-medium: 500;
  --weight-body-bold: 700;

  /* Scale (1920×1080 slide reference; divide ~2 for documents) */
  --text-hero: 96px;        /* single-statement slides */
  --text-h1: 72px;          /* slide titles */
  --text-h2: 48px;          /* section subtitles */
  --text-h3: 34px;          /* card titles */
  --text-body-lg: 26px;     /* lead paragraphs */
  --text-body-md: 20px;     /* standard body */
  --text-eyebrow: 18px;     /* uppercase kickers */

  /* Darker Grotesque has a very tall x-height & short descenders.
     Brand guide: headings 92% line-height; body 130%. */
  --leading-display: 0.92;
  --leading-body: 1.3;
  --tracking-eyebrow: 0.12em;
}
```

## tokens/spacing.css

```css
/* Open Supply Hub — spacing, radii, borders, shadows
   The brand is FLAT: no drop shadows anywhere in the decks.
   Structure comes from color blocks and generous whitespace. */

:root {
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 16px;
  --space-4: 24px;
  --space-5: 40px;
  --space-6: 64px;
  --space-7: 96px;
  --slide-margin: 110px; /* deck side margins at 1920px */

  /* Radii — mostly square; pills for buttons/tags, soft radius for cards */
  --radius-none: 0;
  --radius-card: 16px;
  --radius-pill: 999px;

  /* Borders — thin off-black keylines when separation is needed */
  --border-width: 1.5px;
  --border-keyline: var(--border-width) solid var(--osh-off-black);

  /* Shadows — intentionally none in this brand */
  --shadow-none: none;
}
```

## tokens/fonts.css

```css
/* Open Supply Hub — webfonts
   Variable latin subsets fetched from Google Fonts (exact families used in decks). */

@font-face {
  font-family: "Darker Grotesque";
  font-style: normal;
  font-weight: 300 900;
  font-display: swap;
  src: url("../assets/fonts/DarkerGrotesque-Variable-latin.woff2") format("woff2");
}

@font-face {
  font-family: "DM Sans";
  font-style: normal;
  font-weight: 100 1000;
  font-display: swap;
  src: url("../assets/fonts/DMSans-Variable-latin.woff2") format("woff2");
}

@font-face {
  font-family: "DM Sans";
  font-style: italic;
  font-weight: 100 1000;
  font-display: swap;
  src: url("../assets/fonts/DMSans-Italic-Variable-latin.woff2") format("woff2");
}
```

## tokens/base.css

```css
/* Open Supply Hub — minimal base rules */

body {
  font-family: var(--font-body);
  font-weight: var(--weight-body);
  color: var(--text-body);
  background: var(--surface-page);
  line-height: var(--leading-body);
  margin: 0;
}

h1, h2, h3, h4 {
  font-family: var(--font-display);
  font-weight: var(--weight-display-bold);
  line-height: var(--leading-display);
  color: var(--text-heading);
  margin: 0;
}

a { color: var(--link-color); text-decoration: underline; }
a:hover { color: var(--link-hover-color); }
```

> Fonts: both families are free Google Fonts. In a fresh environment, instead of the local woff2 files use:
> `<link href="https://fonts.googleapis.com/css2?family=Darker+Grotesque:wght@300..900&family=DM+Sans:opsz,wght@9..40,100..1000&display=swap" rel="stylesheet">`


---

# 3. COMPONENTS (React)

## Button

Uppercase pill CTA button used for deck and collateral calls-to-action (e.g. "GET PRICING").

```jsx
<Button variant="accent" size="lg">Get Pricing</Button>
```

Variants: `primary` (off-black), `accent` (purple), `outline`, `inverse` (for dark surfaces). Sizes sm/md/lg. Hover dims to 85% opacity; no shadows.


```jsx
import React from 'react';

/** Pill button in the OSH deck CTA style (e.g. "GET PRICING"). */
export function Button({ variant = 'primary', size = 'md', children, ...rest }) {
  const palettes = {
    primary: { background: 'var(--osh-off-black)', color: 'var(--osh-off-white)', border: '1.5px solid var(--osh-off-black)' },
    accent: { background: 'var(--osh-purple)', color: 'var(--osh-off-white)', border: '1.5px solid var(--osh-purple)' },
    outline: { background: 'transparent', color: 'var(--osh-off-black)', border: '1.5px solid var(--osh-off-black)' },
    inverse: { background: 'var(--osh-off-white)', color: 'var(--osh-off-black)', border: '1.5px solid var(--osh-off-white)' },
  };
  const sizes = {
    sm: { fontSize: 12, padding: '8px 20px' },
    md: { fontSize: 14, padding: '12px 28px' },
    lg: { fontSize: 16, padding: '16px 36px' },
  };
  return (
    <button
      style={{
        fontFamily: 'var(--font-body)',
        fontWeight: 700,
        letterSpacing: '0.08em',
        textTransform: 'uppercase',
        borderRadius: 'var(--radius-pill)',
        cursor: 'pointer',
        ...palettes[variant],
        ...sizes[size],
      }}
      onMouseEnter={(e) => { e.currentTarget.style.opacity = '0.85'; }}
      onMouseLeave={(e) => { e.currentTarget.style.opacity = '1'; }}
      {...rest}
    >
      {children}
    </button>
  );
}
```

## Eyebrow

Uppercase tracked kicker label placed above headlines — the deck wayfinding device ("CASE STUDY", "FEATURES: …", "FIND OUT MORE").

```jsx
<Eyebrow color="var(--osh-purple)">Case Study</Eyebrow>
```


```jsx
import React from 'react';

/** Uppercase tracked kicker label, e.g. "CASE STUDY", "FEATURES: OS HUB SOLUTIONS". */
export function Eyebrow({ color = 'var(--osh-off-black)', children, ...rest }) {
  return (
    <div
      style={{
        fontFamily: 'var(--font-body)',
        textTransform: 'uppercase',
        letterSpacing: 'var(--tracking-eyebrow)',
        fontWeight: 700,
        fontSize: 'var(--text-eyebrow)',
        color,
      }}
      {...rest}
    >
      {children}
    </div>
  );
}
```

## Tag

Solid uppercase pill tag for stakeholder groups and category labels ("BRANDS & RETAILERS", "CIVIL SOCIETY").

```jsx
<Tag color="purple">Brands & Retailers</Tag>
```

Colors: yellow, purple, green, pink, dark, outline.


```jsx
import React from 'react';

/** Small solid tag/chip for stakeholder groups and category labels. */
export function Tag({ color = 'yellow', children, ...rest }) {
  const fills = {
    yellow: { background: 'var(--osh-yellow)', color: 'var(--osh-off-black)' },
    purple: { background: 'var(--osh-purple)', color: 'var(--osh-off-white)' },
    green: { background: 'var(--osh-green)', color: 'var(--osh-off-black)' },
    pink: { background: 'var(--osh-pink)', color: 'var(--osh-off-black)' },
    dark: { background: 'var(--osh-off-black)', color: 'var(--osh-off-white)' },
    outline: { background: 'transparent', color: 'var(--osh-off-black)', border: '1.5px solid var(--osh-off-black)' },
  };
  return (
    <span
      style={{
        display: 'inline-block',
        fontFamily: 'var(--font-body)',
        fontWeight: 700,
        fontSize: 13,
        textTransform: 'uppercase',
        letterSpacing: '0.08em',
        padding: '5px 14px',
        borderRadius: 'var(--radius-pill)',
        ...fills[color],
      }}
      {...rest}
    >
      {children}
    </span>
  );
}
```

## Stat

Big-number stat callout ("2,500,000+ / OS IDs") for community and impact slides.

```jsx
<Stat value="4,500+" label="Data contributors" sublabel="Brands, orgs & service providers" color="var(--osh-green)" />
```


```jsx
import React from 'react';

/** Big-number stat callout, e.g. "2,500,000+ / Production locations listed". */
export function Stat({ value, label, sublabel, color = 'var(--osh-purple)', align = 'center', ...rest }) {
  return (
    <div style={{ textAlign: align, fontFamily: 'var(--font-body)' }} {...rest}>
      <div style={{ fontFamily: 'var(--font-display)', fontWeight: 800, fontSize: 72, lineHeight: 0.9, color }}>{value}</div>
      <div style={{ fontWeight: 700, fontSize: 20, marginTop: 8, color: 'var(--text-body)' }}>{label}</div>
      {sublabel ? <div style={{ fontSize: 15, marginTop: 4, color: 'var(--text-muted)' }}>{sublabel}</div> : null}
    </div>
  );
}
```

## Card

Flat content card: white/off-white/dark/yellow/green-tint fill, 16px radius, optional keyline, never a shadow.

```jsx
<Card tone="yellow" padding={24}>
  <h3>Three Pillars Make It Work</h3>
</Card>
```


```jsx
import React from 'react';

/** Flat content card — white surface, 16px radius, optional off-black keyline. No shadow. */
export function Card({ tone = 'white', keyline = false, padding = 32, children, style, ...rest }) {
  const tones = {
    white: { background: 'var(--surface-card)' },
    offwhite: { background: 'var(--surface-page)' },
    dark: { background: 'var(--surface-page-dark)', color: 'var(--text-inverse)' },
    yellow: { background: 'var(--osh-yellow)' },
    greenTint: { background: 'var(--osh-green-tint)' },
  };
  return (
    <div
      style={{
        borderRadius: 'var(--radius-card)',
        border: keyline ? 'var(--border-keyline)' : 'none',
        padding,
        fontFamily: 'var(--font-body)',
        ...tones[tone],
        ...style,
      }}
      {...rest}
    >
      {children}
    </div>
  );
}
```

## SpeechBubble

Speech-bubble callout in the deck illustration style — solid brand fill, off-black outline, tail. Use for questions and voices ("Where was this made?").

```jsx
<SpeechBubble color="pink">Are the people who made it safe?</SpeechBubble>
```

For pixel-exact bubbles, use the PNG assets in `assets/illustrations/` instead.


```jsx
import React from 'react';

/** Rounded speech-bubble callout with a solid brand fill and off-black outline. */
export function SpeechBubble({ color = 'yellow', children, style, ...rest }) {
  const fills = {
    yellow: 'var(--osh-yellow)',
    pink: 'var(--osh-pink)',
    green: 'var(--osh-green)',
    white: 'var(--osh-white)',
  };
  return (
    <div style={{ position: 'relative', display: 'inline-block', ...style }} {...rest}>
      <div
        style={{
          background: fills[color],
          border: '2px solid var(--osh-off-black)',
          borderRadius: 28,
          padding: '18px 26px',
          fontFamily: 'var(--font-body)',
          fontWeight: 500,
          fontSize: 18,
          color: 'var(--osh-off-black)',
          lineHeight: 1.35,
        }}
      >
        {children}
      </div>
      <svg width="34" height="26" viewBox="0 0 34 26" style={{ position: 'absolute', left: 34, bottom: -22 }} aria-hidden="true">
        <path d="M2 2 C10 2 22 2 30 2 L14 24 C13 14 8 6 2 2 Z" fill={fills[color]} stroke="var(--osh-off-black)" strokeWidth="2" strokeLinejoin="round"></path>
      </svg>
    </div>
  );
}
```


---

# 4. SLIDE LAYOUT LIBRARY (1280×720 HTML)

Each is a complete standalone slide layout. Image paths reference `assets/` — swap for your own copies or remove decorative images.

## slides/BandHeaderSlide.html

```html
<!-- @dsCard group="Slides" viewport="1280x720" name="Band Header (Data)" subtitle="Purple band with star + uppercase title; content canvas below" -->
<!DOCTYPE html>
<html><head><link rel="stylesheet" href="../styles.css">
<style>a{color:var(--link-color)}a:hover{color:var(--link-hover-color)}</style></head>
<body style="margin:0;">
<div data-screen-label="Band Header Data" style="width:1280px;height:720px;background:var(--osh-white);position:relative;overflow:hidden;">
  <div style="height:72px;background:var(--osh-purple);display:flex;align-items:center;gap:18px;padding:0 40px;">
    <img src="../assets/logos/osh-star-white.svg" alt="" style="width:34px;">
    <span style="font-family:var(--font-body);font-weight:700;font-size:20px;color:var(--osh-off-white);letter-spacing:0.08em;text-transform:uppercase;">Cash coverage to monthly expenses</span>
  </div>
  <div style="padding:40px 72px;">
    <div style="height:440px;border:1.5px dashed rgba(13,17,40,0.3);border-radius:12px;display:grid;place-items:center;">
      <span style="font:500 17px 'DM Sans';color:var(--text-muted);">Chart / table area</span>
    </div>
    <p style="font-size:15px;color:var(--text-muted);margin-top:22px;max-width:1000px;">As of March, we have cash on hand to cover approximately nine months of expenses — footnote commentary sits here under the chart.</p>
  </div>
</div>
</body></html>
```

## slides/BigNumberSlide.html

```html
<!-- @dsCard group="Slides" viewport="1280x720" name="Big Number Flow" subtitle="N → N → N reduction/funnel statement" -->
<!DOCTYPE html>
<html><head><link rel="stylesheet" href="../styles.css">
<style>a{color:var(--link-color)}a:hover{color:var(--link-hover-color)}</style></head>
<body style="margin:0;">
<div data-screen-label="Big Number Flow" style="width:1280px;height:720px;background:var(--osh-off-white);position:relative;overflow:hidden;padding:64px 72px;box-sizing:border-box;">
  <div style="height:44px;background:var(--osh-off-black);position:absolute;top:0;left:0;right:0;display:flex;align-items:center;justify-content:flex-end;padding:0 36px;box-sizing:border-box;">
    <span style="font-family:var(--font-body);font-weight:700;font-size:15px;color:var(--osh-off-white);letter-spacing:0.04em;">New Product Update</span>
  </div>
  <h1 style="font-size:44px;font-weight:800;margin-top:44px;">User story focus</h1>
  <p style="font-size:19px;max-width:900px;margin-top:16px;">We collected 44 user stories across the org, down-selected 6 for detailed consideration, and chose 2 priority stories the team felt would drive real change.</p>
  <div style="display:flex;align-items:center;justify-content:center;gap:56px;margin-top:64px;">
    <div style="text-align:center;">
      <div style="font-family:var(--font-display);font-weight:800;font-size:130px;line-height:0.9;color:var(--osh-purple);">44</div>
      <div style="font:600 16px 'DM Sans';margin-top:10px;">collected</div>
    </div>
    <div style="font-family:var(--font-display);font-weight:800;font-size:60px;color:var(--osh-off-black);">→</div>
    <div style="text-align:center;">
      <div style="font-family:var(--font-display);font-weight:800;font-size:130px;line-height:0.9;color:var(--osh-green);">6</div>
      <div style="font:600 16px 'DM Sans';margin-top:10px;">shortlisted</div>
    </div>
    <div style="font-family:var(--font-display);font-weight:800;font-size:60px;color:var(--osh-off-black);">→</div>
    <div style="text-align:center;">
      <div style="font-family:var(--font-display);font-weight:800;font-size:130px;line-height:0.9;color:var(--osh-red);">2</div>
      <div style="font:600 16px 'DM Sans';margin-top:10px;">prototyping</div>
    </div>
  </div>
</div>
</body></html>
```

## slides/CalloutBoxesSlide.html

```html
<!-- @dsCard group="Slides" viewport="1280x720" name="Callout Boxes" subtitle="Pill label + colored rounded panels — strategies/goals layout" -->
<!DOCTYPE html>
<html><head><link rel="stylesheet" href="../styles.css">
<style>a{color:var(--link-color)}a:hover{color:var(--link-hover-color)}
.panel{border-radius:16px;padding:30px 34px;box-sizing:border-box;}
.panel h3{font-size:26px;}
.panel ul{font-size:16px;line-height:1.5;margin:12px 0 0;padding-left:20px;}</style></head>
<body style="margin:0;">
<div data-screen-label="Callout Boxes" style="width:1280px;height:720px;background:var(--osh-off-white);position:relative;overflow:hidden;padding:56px 72px;box-sizing:border-box;">
  <span style="display:inline-block;background:var(--osh-yellow);border:2px solid var(--osh-off-black);border-radius:999px;padding:8px 26px;font-family:var(--font-display);font-weight:800;font-size:26px;line-height:1;">2026 strategies</span>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:28px;margin-top:36px;">
    <div class="panel" style="background:var(--osh-yellow);">
      <h3>Grow revenue</h3>
      <ul><li>Increase reliance on philanthropy for growth</li><li>Build revenue positive tier for commercial users</li></ul>
    </div>
    <div class="panel" style="background:var(--osh-green);">
      <h3>Key priorities</h3>
      <ul><li>Launch Spotlight commercial packages</li><li>Investment in R&amp;D efficiencies</li></ul>
    </div>
    <div class="panel" style="background:var(--osh-pink);">
      <h3>Next steps</h3>
      <ul><li>Grow Spotlight partnerships</li><li>Q2 checkpoint with the board</li></ul>
    </div>
    <div class="panel" style="background:var(--osh-white);border:2px solid var(--osh-off-black);">
      <h3>Open questions</h3>
      <ul><li>What do we need for success?</li><li>Where should we focus most?</li></ul>
    </div>
  </div>
</div>
</body></html>
```

## slides/CaseStudySlide.html

```html
<!-- @dsCard group="Slides" viewport="1280x720" name="Case Study Slide" subtitle="Eyebrow + narrative + pull quote layout" -->
<!DOCTYPE html>
<html><head><link rel="stylesheet" href="../styles.css">
<style>a{color:var(--link-color)}a:hover{color:var(--link-hover-color)}</style></head>
<body style="margin:0;">
<div data-screen-label="Case Study Slide" style="width:1280px;height:720px;background:var(--osh-off-white);position:relative;overflow:hidden;padding:72px;box-sizing:border-box;display:grid;grid-template-columns:1.3fr 1fr;gap:64px;">
  <div>
    <div style="font-family:var(--font-body);font-weight:700;font-size:14px;letter-spacing:0.13em;text-transform:uppercase;">Case Study</div>
    <h1 style="font-size:48px;font-weight:800;margin-top:10px;">More effectively achieving transparency &amp; collaboration goals</h1>
    <p style="font-size:17px;margin-top:22px;">ASOS began sharing their supplier list on OS Hub to amplify the reach of their transparency work — and realized a number of other benefits:</p>
    <ul style="font-size:17px;line-height:1.5;margin-top:12px;padding-left:22px;">
      <li>Visualizing their supply chain internally and externally via the <b>OS Hub Embedded Map</b></li>
      <li>Satisfying requirements of industry initiatives, like the Fashion Transparency Index</li>
      <li>Understanding which other organizations are connected to their suppliers when issues arise</li>
    </ul>
    <a href="https://opensupplyhub.org" style="display:inline-block;margin-top:18px;font-family:var(--font-body);font-weight:700;font-size:14px;letter-spacing:0.13em;text-transform:uppercase;color:var(--osh-purple);">Find Out More →</a>
  </div>
  <div style="display:flex;flex-direction:column;justify-content:center;">
    <div style="background:var(--osh-yellow);border-radius:16px;padding:36px;">
      <p style="font-family:var(--font-display);font-weight:700;font-size:29px;line-height:1.05;margin:0;">&ldquo;Transparency is essential in effectively identifying and addressing risks in our supply chain — after all, we can't manage what we don't know.&rdquo;</p>
      <div style="font-family:var(--font-body);font-weight:700;font-size:15px;margin-top:18px;">ASOS</div>
    </div>
  </div>
</div>
</body></html>
```

## slides/ContactSlide.html

```html
<!-- @dsCard group="Slides" viewport="1280x720" name="Contact Slide" subtitle="Closing vision + contacts" -->
<!DOCTYPE html>
<html><head><link rel="stylesheet" href="../styles.css">
<style>a{color:var(--link-color)}a:hover{color:var(--link-hover-color)}</style></head>
<body style="margin:0;">
<div data-screen-label="Contact Slide" style="width:1280px;height:720px;background:var(--osh-off-white);position:relative;overflow:hidden;padding:72px;box-sizing:border-box;">
  <div style="font-family:var(--font-body);font-weight:700;font-size:14px;letter-spacing:0.13em;text-transform:uppercase;color:var(--osh-purple);">For More Information</div>
  <h1 style="font-size:46px;font-weight:800;margin-top:12px;max-width:880px;">We're only just getting started. Our vision is to map the millions of production locations across the world — for the <span style="color:var(--osh-purple);">100+ million people</span> working in them.</h1>
  <p style="font-size:18px;margin-top:16px;">Reach out to set up a demo or call to learn more.</p>
  <div style="display:flex;gap:80px;margin-top:48px;">
    <div>
      <div style="font-family:var(--font-display);font-weight:700;font-size:30px;">İrem Yanpar Coşdan</div>
      <div style="font-size:16px;margin-top:4px;">Account Manager, Facilities &amp; Trade Associations</div>
      <a href="mailto:irem@opensupplyhub.org" style="font-size:16px;font-weight:700;">irem@opensupplyhub.org</a>
      <div style="font-size:14px;color:var(--text-muted);margin-top:2px;">Based in Türkiye</div>
    </div>
    <div>
      <div style="font-family:var(--font-display);font-weight:700;font-size:30px;">Francesca Romano</div>
      <div style="font-size:16px;margin-top:4px;">Account Manager, Brands &amp; Service Providers</div>
      <a href="mailto:francesca@opensupplyhub.org" style="font-size:16px;font-weight:700;">francesca@opensupplyhub.org</a>
      <div style="font-size:14px;color:var(--text-muted);margin-top:2px;">Based in Germany</div>
    </div>
  </div>
  <img src="../assets/logos/osh-logo-dark.svg" alt="Open Supply Hub" style="position:absolute;left:72px;bottom:56px;width:170px;">
  <div style="position:absolute;right:0;bottom:0;width:620px;height:300px;background:url('../assets/backgrounds/corner-cluster-light.png') right bottom / 210% auto no-repeat;"></div>
</div>
</body></html>
```

## slides/KeyNotesSlide.html

```html
<!-- @dsCard group="Slides" viewport="1280x720" name="Key Notes + Chart" subtitle="Colored key-notes panel left, chart right — KPI deep-dive layout" -->
<!DOCTYPE html>
<html><head><link rel="stylesheet" href="../styles.css">
<style>a{color:var(--link-color)}a:hover{color:var(--link-hover-color)}</style></head>
<body style="margin:0;">
<div data-screen-label="Key Notes Chart" style="width:1280px;height:720px;background:var(--osh-off-white);position:relative;overflow:hidden;">
  <div style="height:44px;background:var(--osh-off-black);display:flex;align-items:center;justify-content:flex-end;padding:0 36px;">
    <span style="font-family:var(--font-body);font-weight:700;font-size:15px;color:var(--osh-off-white);letter-spacing:0.04em;">FY26 KPIs Deep Dive</span>
  </div>
  <div style="display:grid;grid-template-columns:340px 1fr;gap:40px;padding:40px 60px;box-sizing:border-box;">
    <div style="background:var(--osh-yellow);border-radius:14px;padding:28px 30px;height:500px;box-sizing:border-box;">
      <h3 style="font-size:30px;">Key notes</h3>
      <ul style="font-size:16px;line-height:1.5;margin:16px 0 0;padding-left:20px;">
        <li><b>Q1:</b> headline result goes here</li>
        <li>Context on what changed this quarter</li>
        <li>Risk or watch-item to flag for the board</li>
      </ul>
    </div>
    <div style="height:500px;background:var(--osh-white);border:1.5px dashed rgba(13,17,40,0.3);border-radius:12px;display:grid;place-items:center;">
      <span style="font:500 17px 'DM Sans';color:var(--text-muted);">Chart area</span>
    </div>
  </div>
</div>
</body></html>
```

## slides/MotionSlide.html

```html
<!-- @dsCard group="Slides" viewport="1280x720" name="Motion Slide" subtitle="Short statement with climbing shape mosaic — motions/decisions" -->
<!DOCTYPE html>
<html><head><link rel="stylesheet" href="../styles.css">
<style>a{color:var(--link-color)}a:hover{color:var(--link-hover-color)}
.cell{overflow:hidden;display:grid;place-items:center;}
.cell img{width:100%;height:100%;object-fit:contain;}</style></head>
<body style="margin:0;">
<div data-screen-label="Motion Slide" style="width:1280px;height:720px;background:var(--osh-off-white);position:relative;overflow:hidden;">
  <div style="position:absolute;left:72px;top:150px;width:560px;">
    <h1 style="font-size:56px;font-weight:800;color:var(--osh-off-black);">Motion for election</h1>
    <ul style="font-size:19px;line-height:1.5;margin-top:22px;padding-left:22px;">
      <li>To elect [name] to the OS Hub Board of Directors</li>
    </ul>
  </div>
  <div style="position:absolute;right:0;bottom:0;display:grid;grid-template-columns:repeat(4,120px);grid-template-rows:repeat(4,120px);">
    <div class="cell"></div><div class="cell"></div><div class="cell"><img src="../assets/shapes/triangle-red.png" alt=""></div><div class="cell"><img src="../assets/shapes/fan-lines-dark.png" alt=""></div>
    <div class="cell"></div><div class="cell"><img src="../assets/shapes/circle-pink.png" alt=""></div><div class="cell"><img src="../assets/shapes/semicircles-yellow.png" alt=""></div><div class="cell"><img src="../assets/shapes/triangles-green-pair.png" alt=""></div>
    <div class="cell"><img src="../assets/shapes/triangle-yellow.png" alt=""></div><div class="cell"><img src="../assets/shapes/petals-purple.svg" alt=""></div><div class="cell"><img src="../assets/shapes/checkerboard-dark.png" alt=""></div><div class="cell"><img src="../assets/shapes/circle-purple.png" alt=""></div>
    <div class="cell"><img src="../assets/shapes/semicircles-green.png" alt=""></div><div class="cell"><img src="../assets/shapes/triangle-pink.png" alt=""></div><div class="cell"><img src="../assets/shapes/burst-dark.png" alt=""></div><div class="cell"><img src="../assets/shapes/petals-red.png" alt=""></div>
  </div>
</div>
</body></html>
```

## slides/PillarsSlide.html

```html
<!-- @dsCard group="Slides" viewport="1280x720" name="Pillars Slide" subtitle="Three-column content layout" -->
<!DOCTYPE html>
<html><head><link rel="stylesheet" href="../styles.css">
<style>a{color:var(--link-color)}a:hover{color:var(--link-hover-color)}</style></head>
<body style="margin:0;">
<div data-screen-label="Pillars Slide" style="width:1280px;height:720px;background:var(--osh-off-white);position:relative;overflow:hidden;padding:72px;box-sizing:border-box;">
  <div style="font-family:var(--font-body);font-weight:700;font-size:14px;letter-spacing:0.13em;text-transform:uppercase;color:var(--osh-purple);">The Principles Behind a True Solution</div>
  <h1 style="font-size:58px;font-weight:800;margin-top:8px;">Three Pillars Make It Work</h1>
  <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:44px;margin-top:56px;">
    <div>
      <img src="../assets/shapes/circle-purple.png" alt="" style="width:72px;height:72px;">
      <h3 style="font-size:31px;margin-top:20px;">Standardization &amp; Data Exchange</h3>
      <p style="font-size:17px;margin-top:10px;">We need standardized data with <b>universal IDs</b> for each location, so information can be connected and layered.</p>
    </div>
    <div>
      <img src="../assets/shapes/triangle-yellow.png" alt="" style="width:72px;height:72px;object-fit:contain;">
      <h3 style="font-size:31px;margin-top:20px;">Openness &amp; Accessibility</h3>
      <p style="font-size:17px;margin-top:10px;">Everyone starts from the <b>same base dataset</b> and contributes to keeping it up-to-date and accurate.</p>
    </div>
    <div>
      <img src="../assets/shapes/semicircles-green.png" alt="" style="width:72px;height:72px;object-fit:contain;">
      <h3 style="font-size:31px;margin-top:20px;">Engagement &amp; Impact</h3>
      <p style="font-size:17px;margin-top:10px;">See <b>which organizations are connected</b> to build solutions together — we can't solve problems we can't see.</p>
    </div>
  </div>
  <img src="../assets/logos/osh-star-dark.svg" alt="" style="position:absolute;right:64px;top:64px;width:46px;">
</div>
</body></html>
```

## slides/SectionDividerSlide.html

```html
<!-- @dsCard group="Slides" viewport="1280x720" name="Section Divider" subtitle="Numbered section break on dark" -->
<!DOCTYPE html>
<html><head><link rel="stylesheet" href="../styles.css">
<style>a{color:var(--osh-yellow)}a:hover{color:var(--osh-off-white)}</style></head>
<body style="margin:0;">
<div data-screen-label="Section Divider" style="width:1280px;height:720px;background:var(--osh-off-black);position:relative;overflow:hidden;display:grid;place-items:center;">
  <div style="text-align:center;">
    <div style="width:84px;height:84px;border-radius:50%;background:var(--osh-purple);display:grid;place-items:center;margin:0 auto 30px;font-family:var(--font-display);font-weight:800;font-size:44px;color:var(--osh-off-white);padding-bottom:6px;box-sizing:border-box;">2</div>
    <h1 style="font-size:88px;font-weight:800;color:var(--osh-off-white);">Open Data in Action</h1>
  </div>
  <img src="../assets/shapes/petals-yellow.png" alt="" style="position:absolute;left:-30px;bottom:-30px;width:200px;">
  <img src="../assets/shapes/burst-dark.png" alt="" style="position:absolute;right:70px;top:60px;width:120px;filter:invert(1);">
</div>
</body></html>
```

## slides/SectionRailSlide.html

```html
<!-- @dsCard group="Slides" viewport="1280x720" name="Section Header (Shape Rail)" subtitle="Vertical shape rail left, centered heading — most-used board layout" -->
<!DOCTYPE html>
<html><head><link rel="stylesheet" href="../styles.css">
<style>a{color:var(--link-color)}a:hover{color:var(--link-hover-color)}
.cell{display:grid;place-items:center;overflow:hidden;}
.cell img{width:100%;height:100%;object-fit:contain;}</style></head>
<body style="margin:0;">
<div data-screen-label="Section Header" style="width:1280px;height:720px;background:var(--osh-off-white);position:relative;overflow:hidden;display:flex;">
  <div style="width:150px;height:720px;flex:none;display:grid;grid-template-rows:repeat(6,1fr);">
    <div class="cell"><img src="../assets/shapes/fan-lines-dark.png" alt=""></div>
    <div class="cell"><img src="../assets/shapes/semicircles-yellow.png" alt=""></div>
    <div class="cell"><img src="../assets/shapes/triangles-green-pair.png" alt=""></div>
    <div class="cell"><img src="../assets/shapes/checkerboard-dark.png" alt=""></div>
    <div class="cell"><img src="../assets/shapes/circle-purple.png" alt=""></div>
    <div class="cell"><img src="../assets/shapes/triangle-red.png" alt=""></div>
  </div>
  <div style="flex:1;display:grid;place-items:center;">
    <h1 style="font-size:64px;font-weight:800;text-align:center;max-width:760px;">Q1 goals and KPIs report</h1>
  </div>
</div>
</body></html>
```

## slides/StatementSlide.html

```html
<!-- @dsCard group="Slides" viewport="1280x720" name="Statement Slide" subtitle="Single centered statement with corner cluster" -->
<!DOCTYPE html>
<html><head><link rel="stylesheet" href="../styles.css">
<style>a{color:var(--link-color)}a:hover{color:var(--link-hover-color)}</style></head>
<body style="margin:0;">
<div data-screen-label="Statement Slide" style="width:1280px;height:720px;background:var(--osh-off-white) url('../assets/backgrounds/corner-cluster-light.png') right bottom / cover no-repeat;position:relative;overflow:hidden;display:grid;place-items:center;">
  <h1 style="font-size:66px;font-weight:800;max-width:900px;text-align:center;padding:0 90px;">Every product comes from a supply chain. <span style="color:var(--osh-purple);">We're all linked</span> with the people and places where our stuff comes from.</h1>
  <img src="../assets/logos/osh-star-dark.svg" alt="" style="position:absolute;top:52px;left:64px;width:54px;">
</div>
</body></html>
```

## slides/StatsSlide.html

```html
<!-- @dsCard group="Slides" viewport="1280x720" name="Stats Slide" subtitle="Big-number community stats" -->
<!DOCTYPE html>
<html><head><link rel="stylesheet" href="../styles.css">
<style>a{color:var(--link-color)}a:hover{color:var(--link-hover-color)}</style></head>
<body style="margin:0;">
<div data-screen-label="Stats Slide" style="width:1280px;height:720px;background:var(--osh-off-white);position:relative;overflow:hidden;padding:80px 72px;box-sizing:border-box;">
  <h1 style="font-size:58px;font-weight:800;">A Dynamic, Growing Community</h1>
  <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:44px;margin-top:90px;text-align:center;">
    <div>
      <div style="font-family:var(--font-display);font-weight:800;font-size:84px;line-height:0.9;color:var(--osh-purple);">2,500,000+</div>
      <div style="font-family:var(--font-body);font-weight:700;font-size:22px;margin-top:14px;">OS IDs</div>
      <p style="font-size:16px;margin-top:6px;color:var(--text-muted);">Production locations listed on OS Hub</p>
    </div>
    <div>
      <div style="font-family:var(--font-display);font-weight:800;font-size:84px;line-height:0.9;color:var(--osh-green);">3,700+</div>
      <div style="font-family:var(--font-body);font-weight:700;font-size:22px;margin-top:14px;">Claimed Profiles</div>
      <p style="font-size:16px;margin-top:6px;color:var(--text-muted);">Facilities &amp; suppliers taking ownership of their data</p>
    </div>
    <div>
      <div style="font-family:var(--font-display);font-weight:800;font-size:84px;line-height:0.9;color:var(--osh-red);">4,500+</div>
      <div style="font-family:var(--font-body);font-weight:700;font-size:22px;margin-top:14px;">Data Contributors</div>
      <p style="font-size:16px;margin-top:6px;color:var(--text-muted);">Brands, orgs &amp; service providers connecting with suppliers</p>
    </div>
  </div>
  <img src="../assets/backgrounds/confetti-strip-light.png" alt="" style="position:absolute;left:0;bottom:0;width:100%;">
</div>
</body></html>
```

## slides/TitleSlide.html

```html
<!-- @dsCard group="Slides" viewport="1280x720" name="Title Slide" subtitle="Dark mosaic title — from the LUPC deck" -->
<!DOCTYPE html>
<html><head><link rel="stylesheet" href="../styles.css">
<style>a{color:var(--osh-yellow)}a:hover{color:var(--osh-off-white)}</style></head>
<body style="margin:0;">
<div data-screen-label="Title Slide" style="width:1280px;height:720px;background:var(--osh-off-black) url('../assets/backgrounds/mosaic-dark.png') right center / cover no-repeat;position:relative;overflow:hidden;">
  <img src="../assets/logos/osh-logo-white.svg" alt="Open Supply Hub" style="position:absolute;top:64px;left:74px;width:200px;">
  <div style="position:absolute;left:74px;bottom:180px;width:620px;">
    <div style="font-family:var(--font-body);font-weight:700;font-size:15px;letter-spacing:0.14em;text-transform:uppercase;color:var(--osh-yellow);margin-bottom:18px;">Supply Chain Mapping · July 2026</div>
    <h1 style="font-size:64px;font-weight:800;color:var(--osh-off-white);">What is Open Supply Hub, and how can it support transparency?</h1>
  </div>
  <div style="position:absolute;left:74px;bottom:64px;font-family:var(--font-body);font-weight:500;font-size:17px;color:var(--osh-off-white);">Responsible Procurement Exchange, LUPC</div>
</div>
</body></html>
```

## slides/TitleSlideLight.html

```html
<!-- @dsCard group="Slides" viewport="1280x720" name="Title Slide (Light)" subtitle="Cream title with logo and mosaic corners — board deck style" -->
<!DOCTYPE html>
<html><head><link rel="stylesheet" href="../styles.css">
<style>a{color:var(--link-color)}a:hover{color:var(--link-hover-color)}</style></head>
<body style="margin:0;">
<div data-screen-label="Title Slide Light" style="width:1280px;height:720px;background:var(--osh-off-white);position:relative;overflow:hidden;">
  <img src="../assets/logos/osh-logo-dark.svg" alt="Open Supply Hub" style="position:absolute;top:56px;left:64px;width:150px;">
  <div style="position:absolute;left:64px;top:240px;width:640px;">
    <h1 style="font-size:56px;font-weight:800;">Open Supply Hub<br>Board of Directors<br>Q1 Meeting</h1>
    <p style="font-size:19px;margin-top:26px;">30 April 2026</p>
  </div>
  <div style="position:absolute;right:0;top:0;width:460px;height:720px;background:url('../assets/backgrounds/mosaic-light.png') right center / cover no-repeat;"></div>
</div>
</body></html>
```

## slides/TopicBarSlide.html

```html
<!-- @dsCard group="Slides" viewport="1280x720" name="Topic Bar Content" subtitle="Navy top bar with running kicker; title + bullets below" -->
<!DOCTYPE html>
<html><head><link rel="stylesheet" href="../styles.css">
<style>a{color:var(--link-color)}a:hover{color:var(--link-hover-color)}</style></head>
<body style="margin:0;">
<div data-screen-label="Topic Bar Content" style="width:1280px;height:720px;background:var(--osh-off-white);position:relative;overflow:hidden;">
  <div style="height:44px;background:var(--osh-off-black);display:flex;align-items:center;justify-content:flex-end;padding:0 36px;">
    <span style="font-family:var(--font-body);font-weight:700;font-size:15px;color:var(--osh-off-white);letter-spacing:0.04em;">FY26 KPIs Deep Dive</span>
  </div>
  <div style="padding:52px 72px;">
    <h1 style="font-size:44px;font-weight:800;">Our new KPI approach</h1>
    <div style="background:var(--osh-pink);border-radius:14px;padding:32px 40px;margin-top:34px;max-width:880px;">
      <p style="font-size:19px;margin:0;">In 2026, we intentionally reduced the number of KPIs we track. The goals were:</p>
      <ul style="font-size:19px;line-height:1.55;margin:14px 0 0;padding-left:24px;">
        <li>Prioritize metrics that actually drive internal action</li>
        <li>Reduce reporting burden on the team</li>
        <li>Create space to complete our Data Quality Dashboard goal</li>
      </ul>
    </div>
  </div>
  <img src="../assets/logos/osh-star-dark.svg" alt="" style="position:absolute;right:36px;top:64px;width:40px;">
</div>
</body></html>
```


---

# 5. SVG ASSETS (inline)

Save each block to the given path.

## assets/logos/osh-logo-dark.svg

```svg
<?xml version="1.0"?><svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" contentScriptType="text/ecmascript" fill="#000000" width="972.96" zoomAndPan="magnify" contentStyleType="text/css" viewBox="0 0 972.96 364.15" height="364.15" preserveAspectRatio="xMidYMid meet" version="1"><g data-name="Layer 2"><g fill="#0d1128" data-name="Layer 1"><path d="M360,2.38H231.89L180,92.27,128.11,2.38H0V130.49l89.89,51.89L0,234.27V362.38H128.11L180,272.5l51.89,89.88H360V234.27l-89.88-51.89L360,130.49Zm-270.58,344L16,273,116.28,246.1ZM16,91.8l73.4-73.4,26.86,100.26ZM180,242.39a60,60,0,1,1,60-60A60,60,0,0,1,180,242.39ZM344,273l-73.39,73.39L243.72,246.1ZM243.72,118.66,270.59,18.4,344,91.8Z"></path><path d="M470.76,115.36q-27.7,0-42.35-15.33T413.77,58q0-17.61,6.33-30.57a46,46,0,0,1,19-20.19Q451.76,0,470.76,0q27.71,0,42.15,15.73T527.35,58q0,17.21-6.43,30.37a44.81,44.81,0,0,1-19,20.09Q489.35,115.35,470.76,115.36Zm-.4-26.71q10.09,0,16.72-3.86A23.81,23.81,0,0,0,497,73.71,37.86,37.86,0,0,0,500.24,58,39,39,0,0,0,497,42a26.68,26.68,0,0,0-9.9-11.67q-6.63-4.35-16.72-4.36-14.44,0-22.06,9.1t-7.62,23A37.19,37.19,0,0,0,444,73.51a24.5,24.5,0,0,0,9.79,11.18Q460.27,88.65,470.36,88.65Z"></path><path d="M562,113.38H534.27V2h47.1q19,0,30,9.79t11,29.39q0,16.62-11.28,26.22T581.37,77H562Zm15.23-89.24H562V57.58h15.23a23.8,23.8,0,0,0,14.25-4.25q5.94-4.26,5.94-12.57,0-8.5-5.84-12.56A24.57,24.57,0,0,0,577.21,24.14Z"></path><path d="M655.77,91.42h59.36v22H628.66V2H713V25.53H655.77V45.91h42.54V68.07H655.77Z"></path><path d="M796.06,2H825v111.4h-53L751.14,14.05h-.39v99.33h-28.7V2h49.08l24.53,99.33h.4Z"></path><path d="M470,239.75a79.65,79.65,0,0,1-18.6-2.17,50.74,50.74,0,0,1-16.43-7A37.09,37.09,0,0,1,423.17,218q-4.46-7.73-4.45-18.6h27.7a12.37,12.37,0,0,0,.89,3.66,15.27,15.27,0,0,0,3.56,5.24,20.52,20.52,0,0,0,7.72,4.66q5,1.88,13.55,1.88a51.48,51.48,0,0,0,7.72-.6,15.91,15.91,0,0,0,6.73-2.48,6.56,6.56,0,0,0,2.77-5.83,7.33,7.33,0,0,0-3.86-6.53,34.53,34.53,0,0,0-10.09-3.86q-6.24-1.49-13.66-3.07a144.68,144.68,0,0,1-14.74-4,52.86,52.86,0,0,1-13.35-6.43,27.21,27.21,0,0,1-9.3-10.48q-3.27-6.43-2.68-16.13,1-14.64,13.86-22.86t35.81-8.21a61,61,0,0,1,23,4.36A41.14,41.14,0,0,1,512,142q6.84,8.91,6.83,22.56H492.13q0-6.13-4.06-9.2a22.28,22.28,0,0,0-9.69-4.06,60.53,60.53,0,0,0-10.19-1A35.53,35.53,0,0,0,456,152.1a6.77,6.77,0,0,0-4.85,6.92,7.84,7.84,0,0,0,4,7A34,34,0,0,0,465.42,170q6.33,1.49,13.95,3t15.13,3.66a51.57,51.57,0,0,1,13.56,6,27.68,27.68,0,0,1,9.5,10.19q3.45,6.33,2.67,16.23-1,14.43-14.55,22.55T470,239.75Z"></path><path d="M577.41,239.75q-24.93,0-37.69-12.76T527,190.29V126.37h29.68v63.72q0,8.31,2.17,13.16a17.58,17.58,0,0,0,5.44,7.22,13.39,13.39,0,0,0,6.83,2.67c2.38.2,4.48.3,6.33.3a46.89,46.89,0,0,0,9.4-1q4.85-1,8.21-6.14t3.37-16.22V126.37h29.68v63.92q0,24.33-12.57,36.9T577.41,239.75Z"></path><path d="M663.69,237.78H636V126.37h47.1q19,0,30,9.8t11,29.38q0,16.62-11.28,26.22t-29.68,9.6H663.69Zm15.23-89.25H663.69V182h15.23a23.8,23.8,0,0,0,14.25-4.25q5.94-4.26,5.94-12.56,0-8.5-5.84-12.57A24.57,24.57,0,0,0,678.92,148.53Z"></path><path d="M756.69,237.78H729V126.37h47.1q19,0,30,9.8t11,29.38q0,16.62-11.28,26.22t-29.68,9.6H756.69Zm15.23-89.25H756.69V182h15.23a23.8,23.8,0,0,0,14.25-4.25q5.94-4.26,5.94-12.56,0-8.5-5.84-12.57A24.57,24.57,0,0,0,771.92,148.53Z"></path><path d="M822.78,237.78V126.37h27.7v87.86h48.08v23.55Z"></path><path d="M906.48,237.78V199.39h-.2l-37.8-73h31.07L920.72,176l21.17-49.67H973l-39,73v38.39Z"></path><path d="M448.6,362.17H420.89V250.77H448.6v44.91h42.54V250.77h27.7v111.4h-27.7V316.66H448.6Z"></path><path d="M577.21,364.15q-24.93,0-37.69-12.77t-12.77-36.7V250.77h29.69v63.71q0,8.31,2.17,13.16a17.58,17.58,0,0,0,5.44,7.22,13.4,13.4,0,0,0,6.83,2.68q3.55.29,6.33.29a46.17,46.17,0,0,0,9.4-1q4.85-1,8.21-6.13t3.37-16.23V250.77h29.68v63.91q0,24.33-12.57,36.9T577.21,364.15Z"></path><path d="M635.58,362.17V250.77h57.78a47.26,47.26,0,0,1,11.88,1.58,44.16,44.16,0,0,1,11.47,4.75,24.93,24.93,0,0,1,8.71,8.7q3.36,5.55,3.36,14.25a26.68,26.68,0,0,1-2.57,11.68q-2.57,5.34-9.2,9.1t-19.29,3.76v1q14.44.39,22.36,3.95t11.08,9.21a26,26,0,0,1,3.17,13q0,9.1-3.57,14.94a24.59,24.59,0,0,1-9.4,9,53,53,0,0,1-12.66,4.85,56.19,56.19,0,0,1-13.46,1.68H635.58Zm27.11-67.48h17.42a82.14,82.14,0,0,0,9.89-.59,18.55,18.55,0,0,0,8.31-2.87c2.24-1.51,3.36-4.12,3.36-7.81s-1-6.07-3.06-7.52a17,17,0,0,0-8-2.73,96.71,96.71,0,0,0-10.48-.54H662.69Zm.2,45.81H681.1a105.52,105.52,0,0,0,12-.64,18.5,18.5,0,0,0,9.2-3.32q3.56-2.67,3.56-9t-3.46-8.9a16.88,16.88,0,0,0-9.1-3q-5.64-.39-12.17-.4H662.89Z"></path></g></g></svg>
```

## assets/logos/osh-logo-white.svg

```svg
<?xml version="1.0"?><svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" contentScriptType="text/ecmascript" fill="#000000" width="972.96" zoomAndPan="magnify" contentStyleType="text/css" viewBox="0 0 972.96 364.15" height="364.15" preserveAspectRatio="xMidYMid meet" version="1"><g data-name="Layer 2"><g fill="#ffffff" data-name="Layer 1"><path d="M360,2.38H231.89L180,92.27,128.11,2.38H0V130.49l89.89,51.89L0,234.27V362.38H128.11L180,272.5l51.89,89.88H360V234.27l-89.88-51.89L360,130.49Zm-270.58,344L16,273,116.28,246.1ZM16,91.8l73.4-73.4,26.86,100.26ZM180,242.39a60,60,0,1,1,60-60A60,60,0,0,1,180,242.39ZM344,273l-73.39,73.39L243.72,246.1ZM243.72,118.66,270.59,18.4,344,91.8Z"></path><path d="M470.76,115.36q-27.7,0-42.35-15.33T413.77,58q0-17.61,6.33-30.57a46,46,0,0,1,19-20.19Q451.76,0,470.76,0q27.71,0,42.15,15.73T527.35,58q0,17.21-6.43,30.37a44.81,44.81,0,0,1-19,20.09Q489.35,115.35,470.76,115.36Zm-.4-26.71q10.09,0,16.72-3.86A23.81,23.81,0,0,0,497,73.71,37.86,37.86,0,0,0,500.24,58,39,39,0,0,0,497,42a26.68,26.68,0,0,0-9.9-11.67q-6.63-4.35-16.72-4.36-14.44,0-22.06,9.1t-7.62,23A37.19,37.19,0,0,0,444,73.51a24.5,24.5,0,0,0,9.79,11.18Q460.27,88.65,470.36,88.65Z"></path><path d="M562,113.38H534.27V2h47.1q19,0,30,9.79t11,29.39q0,16.62-11.28,26.22T581.37,77H562Zm15.23-89.24H562V57.58h15.23a23.8,23.8,0,0,0,14.25-4.25q5.94-4.26,5.94-12.57,0-8.5-5.84-12.56A24.57,24.57,0,0,0,577.21,24.14Z"></path><path d="M655.77,91.42h59.36v22H628.66V2H713V25.53H655.77V45.91h42.54V68.07H655.77Z"></path><path d="M796.06,2H825v111.4h-53L751.14,14.05h-.39v99.33h-28.7V2h49.08l24.53,99.33h.4Z"></path><path d="M470,239.75a79.65,79.65,0,0,1-18.6-2.17,50.74,50.74,0,0,1-16.43-7A37.09,37.09,0,0,1,423.17,218q-4.46-7.73-4.45-18.6h27.7a12.37,12.37,0,0,0,.89,3.66,15.27,15.27,0,0,0,3.56,5.24,20.52,20.52,0,0,0,7.72,4.66q5,1.88,13.55,1.88a51.48,51.48,0,0,0,7.72-.6,15.91,15.91,0,0,0,6.73-2.48,6.56,6.56,0,0,0,2.77-5.83,7.33,7.33,0,0,0-3.86-6.53,34.53,34.53,0,0,0-10.09-3.86q-6.24-1.49-13.66-3.07a144.68,144.68,0,0,1-14.74-4,52.86,52.86,0,0,1-13.35-6.43,27.21,27.21,0,0,1-9.3-10.48q-3.27-6.43-2.68-16.13,1-14.64,13.86-22.86t35.81-8.21a61,61,0,0,1,23,4.36A41.14,41.14,0,0,1,512,142q6.84,8.91,6.83,22.56H492.13q0-6.13-4.06-9.2a22.28,22.28,0,0,0-9.69-4.06,60.53,60.53,0,0,0-10.19-1A35.53,35.53,0,0,0,456,152.1a6.77,6.77,0,0,0-4.85,6.92,7.84,7.84,0,0,0,4,7A34,34,0,0,0,465.42,170q6.33,1.49,13.95,3t15.13,3.66a51.57,51.57,0,0,1,13.56,6,27.68,27.68,0,0,1,9.5,10.19q3.45,6.33,2.67,16.23-1,14.43-14.55,22.55T470,239.75Z"></path><path d="M577.41,239.75q-24.93,0-37.69-12.76T527,190.29V126.37h29.68v63.72q0,8.31,2.17,13.16a17.58,17.58,0,0,0,5.44,7.22,13.39,13.39,0,0,0,6.83,2.67c2.38.2,4.48.3,6.33.3a46.89,46.89,0,0,0,9.4-1q4.85-1,8.21-6.14t3.37-16.22V126.37h29.68v63.92q0,24.33-12.57,36.9T577.41,239.75Z"></path><path d="M663.69,237.78H636V126.37h47.1q19,0,30,9.8t11,29.38q0,16.62-11.28,26.22t-29.68,9.6H663.69Zm15.23-89.25H663.69V182h15.23a23.8,23.8,0,0,0,14.25-4.25q5.94-4.26,5.94-12.56,0-8.5-5.84-12.57A24.57,24.57,0,0,0,678.92,148.53Z"></path><path d="M756.69,237.78H729V126.37h47.1q19,0,30,9.8t11,29.38q0,16.62-11.28,26.22t-29.68,9.6H756.69Zm15.23-89.25H756.69V182h15.23a23.8,23.8,0,0,0,14.25-4.25q5.94-4.26,5.94-12.56,0-8.5-5.84-12.57A24.57,24.57,0,0,0,771.92,148.53Z"></path><path d="M822.78,237.78V126.37h27.7v87.86h48.08v23.55Z"></path><path d="M906.48,237.78V199.39h-.2l-37.8-73h31.07L920.72,176l21.17-49.67H973l-39,73v38.39Z"></path><path d="M448.6,362.17H420.89V250.77H448.6v44.91h42.54V250.77h27.7v111.4h-27.7V316.66H448.6Z"></path><path d="M577.21,364.15q-24.93,0-37.69-12.77t-12.77-36.7V250.77h29.69v63.71q0,8.31,2.17,13.16a17.58,17.58,0,0,0,5.44,7.22,13.4,13.4,0,0,0,6.83,2.68q3.55.29,6.33.29a46.17,46.17,0,0,0,9.4-1q4.85-1,8.21-6.13t3.37-16.23V250.77h29.68v63.91q0,24.33-12.57,36.9T577.21,364.15Z"></path><path d="M635.58,362.17V250.77h57.78a47.26,47.26,0,0,1,11.88,1.58,44.16,44.16,0,0,1,11.47,4.75,24.93,24.93,0,0,1,8.71,8.7q3.36,5.55,3.36,14.25a26.68,26.68,0,0,1-2.57,11.68q-2.57,5.34-9.2,9.1t-19.29,3.76v1q14.44.39,22.36,3.95t11.08,9.21a26,26,0,0,1,3.17,13q0,9.1-3.57,14.94a24.59,24.59,0,0,1-9.4,9,53,53,0,0,1-12.66,4.85,56.19,56.19,0,0,1-13.46,1.68H635.58Zm27.11-67.48h17.42a82.14,82.14,0,0,0,9.89-.59,18.55,18.55,0,0,0,8.31-2.87c2.24-1.51,3.36-4.12,3.36-7.81s-1-6.07-3.06-7.52a17,17,0,0,0-8-2.73,96.71,96.71,0,0,0-10.48-.54H662.69Zm.2,45.81H681.1a105.52,105.52,0,0,0,12-.64,18.5,18.5,0,0,0,9.2-3.32q3.56-2.67,3.56-9t-3.46-8.9a16.88,16.88,0,0,0-9.1-3q-5.64-.39-12.17-.4H662.89Z"></path></g></g></svg>
```

## assets/logos/osh-star-dark.svg

```svg
<?xml version="1.0"?><svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" contentScriptType="text/ecmascript" fill="none" width="300" zoomAndPan="magnify" style="fill: none" contentStyleType="text/css" viewBox="0 0 300 300" height="300" preserveAspectRatio="xMidYMid meet" version="1"><path fill="#0d1128" d="M300 0H193.242L150 74.9167L106.758 0H0V106.758L74.9083 150L0 193.25V300H106.758L150 225.1L193.242 300H300V193.25L225.1 150L300 106.758V0ZM74.5167 286.667L13.3333 225.5L96.8833 203.108L74.5167 286.667ZM13.3333 74.525L74.5 13.3584L96.8833 96.9084L13.3333 74.525ZM150 200C140.111 200 130.444 197.068 122.221 191.573C113.999 186.079 107.59 178.271 103.806 169.134C100.022 159.998 99.0314 149.945 100.961 140.245C102.89 130.546 107.652 121.637 114.645 114.645C121.637 107.652 130.546 102.89 140.245 100.961C149.945 99.0314 159.998 100.022 169.134 103.806C178.271 107.59 186.079 113.999 191.573 122.221C197.068 130.444 200 140.111 200 150C200 163.261 194.732 175.979 185.355 185.355C175.979 194.732 163.261 200 150 200ZM286.667 225.483L225.492 286.667L203.1 203.117L286.667 225.483ZM203.117 96.8917L225.492 13.3333L286.65 74.5L203.117 96.8917Z"></path></svg>
```

## assets/logos/osh-star-white.svg

```svg
<?xml version="1.0"?><svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" contentScriptType="text/ecmascript" fill="none" width="300" zoomAndPan="magnify" style="fill: none" contentStyleType="text/css" viewBox="0 0 300 300" height="300" preserveAspectRatio="xMidYMid meet" version="1"><path fill="#ffffff" d="M300 0H193.242L150 74.9167L106.758 0H0V106.758L74.9083 150L0 193.25V300H106.758L150 225.1L193.242 300H300V193.25L225.1 150L300 106.758V0ZM74.5167 286.667L13.3333 225.5L96.8833 203.108L74.5167 286.667ZM13.3333 74.525L74.5 13.3584L96.8833 96.9084L13.3333 74.525ZM150 200C140.111 200 130.444 197.068 122.221 191.573C113.999 186.079 107.59 178.271 103.806 169.134C100.022 159.998 99.0314 149.945 100.961 140.245C102.89 130.546 107.652 121.637 114.645 114.645C121.637 107.652 130.546 102.89 140.245 100.961C149.945 99.0314 159.998 100.022 169.134 103.806C178.271 107.59 186.079 113.999 191.573 122.221C197.068 130.444 200 140.111 200 150C200 163.261 194.732 175.979 185.355 185.355C175.979 194.732 163.261 200 150 200ZM286.667 225.483L225.492 286.667L203.1 203.117L286.667 225.483ZM203.117 96.8917L225.492 13.3333L286.65 74.5L203.117 96.8917Z"></path></svg>
```

## assets/shapes/petals-purple.svg

```svg
<?xml version="1.0"?><svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" contentScriptType="text/ecmascript" fill="#000000" width="269.2" zoomAndPan="magnify" contentStyleType="text/css" viewBox="7.7 20.8 269.2 76.3" height="76.3" preserveAspectRatio="xMidYMid meet" version="1"><g fill="#fccf3f" id="change1_1"><path fill="inherit" d="M11.54,23.02c-0.14,0.19-0.16,0.4-0.07,0.62c-0.54,0.62-1.78,0.14-1.99,1.28l0,0 c-1.82,1.81-1.13,3.66-0.05,5.49c3.04,5.12,6.85,9.64,10.94,13.93c14.66,15.35,31.85,26.93,51.27,35.58 c33.9,15.11,68.89,17.2,104.76,9.82c16.63-3.42,32.35-9.68,47.78-16.67c9.07-4.11,17.86-8.75,26.77-13.18c0,0,0,0,0,0 c0.25-0.3,0.49-0.6,0.74-0.9c0.44-0.02,0.93-0.17,1.29-0.01c0,0,0,0,0.01,0.01c0.28,0.13,0.09,0.53-0.23,0.69 c-1.73,3.5-4.14,6.52-6.71,9.41c-1.76,1.98-3.32,4.03-4.24,6.53c-3.82,4.23-3.95,8.76-0.55,12.7c10.61-4.09,17.08-12.5,22.96-21.59 c2.19-3.38,4.6-6.6,6.96-9.86c5.66-7.8,4.4-6.99,1.27-14.18c-0.7-1.61-1.76-3.03-2.96-4.33c-0.44-0.48-0.89-0.88-1.58-0.88l0,0 c-0.9-1.79-2.58-1.81-4.22-1.75c-4.87,0.18-9.73,0.42-14.6,0.64c-1.02-0.56-2.08-0.39-3.14-0.17c-1-0.6-2.07-0.41-3.13-0.27 c-0.64-0.54-1.44-0.34-2.17-0.44c-9.89-1.39-19.48-3.87-28.62-7.98c-0.69-0.31-1.4-0.56-2.1-0.84c-0.83-0.34-1.77-0.73-2.43,0.05 c-0.5,0.59-0.36,1.66,0.08,2.15c1.94,2.18,2.23,5.19,3.92,7.46c0.75,1.01,1.85,1.63,2.98,2.24c8.69,4.75,17.98,7.83,27.61,9.97 c0.86,0.19,1.77,0.25,2.56,0.61c0.92,0.42,0.66,1.2,0.2,1.89c-1-0.12-1.71,0.28-2.17,1.15c-0.93,0.07-1.83,0.21-2.3,1.18 c0,0,0,0,0,0c-0.23-0.11-0.38-0.04-0.45,0.2c-0.89,0.04-1.71,0.22-2.19,1.09c-0.6,0.16-1.23,0.24-1.79,0.5 c-6.15,2.82-12.25,5.74-18.43,8.49c-5.61,2.5-11.29,4.82-16.94,7.21c0,0,0,0,0,0c-1.57,0.45-3.15,0.84-4.69,1.35 c-15.02,4.87-30.4,7.86-46.19,8.54c-5.64,0.24-11.28,0.31-16.92,0.45c-1.07-0.6-2.17-0.36-3.28-0.14c-1.01-0.6-2.06-0.39-3.12-0.19 c-0.92-0.64-1.92-0.37-2.91-0.27c-0.57-0.48-1.2-0.45-1.85-0.22c-0.22-0.16-0.44-0.17-0.67-0.02c-0.64-0.52-1.43-0.34-2.15-0.46 c-3.56-0.61-7.21-0.58-10.7-1.63c-0.31,0.29-1.34,0.44-0.08,0.97c0.84,0.36,0.89,0.61,0.66,0.82c-0.2,0.18-0.61,0.33-0.91,0.48 c-11.18-2.28-21.95-5.88-32.49-10.19c0,0,0,0,0,0c0,0,0,0,0,0c-0.94-0.49-1.89-0.98-2.83-1.47c-5.62-2.93-11.25-5.86-16.87-8.78 c-0.11-0.24-0.27-0.4-0.47-0.49c-0.14-0.06-0.29-0.09-0.46-0.09c-0.18-0.39-0.49-0.57-0.91-0.56c-0.17-0.4-0.48-0.58-0.91-0.56 c-0.16-0.41-0.47-0.59-0.91-0.57c-0.16-0.41-0.46-0.61-0.9-0.58c-0.15-0.42-0.45-0.61-0.89-0.58l-0.01-0.01 c-0.14-0.41-0.44-0.61-0.87-0.58l-0.02-0.01c-0.27-0.21-0.56-0.41-0.86-0.59l-0.03-0.02c-0.14-0.41-0.42-0.61-0.86-0.59l-0.03-0.02 c-0.14-0.41-0.42-0.61-0.86-0.59l-0.03-0.02c0,0-0.01-0.01-0.01-0.01c0,0,0.01,0.01,0.01,0.01c-0.13-0.42-0.42-0.62-0.86-0.6 l-0.02-0.01c0,0,0,0,0,0c0,0,0,0,0,0c-0.13-0.42-0.42-0.62-0.86-0.6l-0.01-0.01c0,0,0,0,0,0c-0.14-0.42-0.43-0.63-0.87-0.62 c-2.56-2.07-5.11-4.14-7.67-6.21c0,0,0,0,0,0c0,0,0,0,0,0c-1.67-0.66-2.82-2.01-4.11-3.16c0.05-0.2,0.14-0.36,0.25-0.5 c0.17-0.22,0.39-0.37,0.69-0.46c-0.88-0.97-1.69-2.01-2.96-2.52c-0.4-0.12-0.77-0.29-1.06-0.61l0,0c0.35,0.2,0.7,0.41,1.06,0.61 c-0.22-0.37-0.47-0.69-0.94-0.62c-0.12-0.65-0.53-1.04-1.13-1.28c-0.07-0.42-0.29-0.68-0.74-0.7c-0.18-0.4-0.42-0.71-0.89-0.76 c-0.06-0.21-0.17-0.37-0.39-0.46c-0.69-1.1-1.57-2-2.67-2.69c-0.53-0.75-1.04-1.52-1.91-1.93c-0.16-0.6-0.65-0.92-1.1-1.27l0,0 c-2.08-2.96-4.69-5.52-6.28-9.03C13.22,21.85,11.76,21.67,11.54,23.02z M240.06,54.31c-0.01,0-0.01,0-0.02,0 c0,0.01,0.01,0.01,0.01,0.01c-0.01,0-0.02-0.01-0.02-0.01c0,0,0.01,0,0.01,0c0-0.01,0-0.02-0.01-0.03 C240.05,54.29,240.05,54.3,240.06,54.31z M44.66,55.46c0.06,0.06,0.12,0.12,0.18,0.18c-0.02-0.01-0.04-0.02-0.06-0.03 c-0.06-0.04-0.12-0.08-0.18-0.13C44.61,55.48,44.63,55.47,44.66,55.46z M55.52,60.1C55.52,60.1,55.52,60.1,55.52,60.1 c0,0.01-0.01,0.01-0.01,0.02c-0.02,0.02-0.03,0.05-0.05,0.07l-0.07,0.07l0.12-0.15c0-0.01-0.01-0.01-0.01-0.02 C55.5,60.1,55.51,60.1,55.52,60.1z M44.29,55.6c0.1-0.04,0.2-0.08,0.29-0.11c0.06,0.04,0.12,0.08,0.18,0.12 C44.62,55.54,44.46,55.53,44.29,55.6z M45.15,55.9c0.07,0.05,0.14,0.1,0.2,0.15c0,0.01,0.01,0.01,0.01,0.02 C45.29,56.01,45.22,55.95,45.15,55.9z M13.45,29.59c-0.01,0-0.02-0.01-0.03-0.01c0,0-0.01-0.01-0.01-0.01 c0-0.01-0.01-0.02-0.01-0.03C13.42,29.55,13.43,29.57,13.45,29.59z M14.38,30.9C14.38,30.9,14.38,30.9,14.38,30.9 c0,0.02,0,0.04,0.02,0.05C14.4,30.93,14.38,30.91,14.38,30.9z M28.43,38.87c-0.07,0.03-0.14,0.07-0.21,0.13 c-0.01-0.05-0.02-0.1-0.03-0.15C28.27,38.86,28.35,38.86,28.43,38.87z M26.64,36.66c-0.11-0.08-0.19-0.2-0.24-0.35c0,0,0,0,0.01,0 C26.47,36.45,26.54,36.57,26.64,36.66z"></path><path fill="inherit" d="M48.31,55.46c0.29,0.2,0.58,0.39,0.86,0.59C49.03,55.63,48.74,55.44,48.31,55.46z"></path></g></svg>
```

## assets/illustrations/car-yellow.svg

```svg
<?xml version="1.0"?><svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" contentScriptType="text/ecmascript" fill="#fccf3f" width="120.1" zoomAndPan="magnify" contentStyleType="text/css" viewBox="4.0 30.9 120.1 66.3" height="66.3" preserveAspectRatio="xMidYMid meet" version="1"><g id="change1_1"><path fill="inherit" d="M 10.6875 48.539062 C 10.816406 47.90625 10.183594 47.269531 9.679688 46.796875 C 9.296875 47.210938 8.972656 47.660156 8.761719 48.171875 C 8.5625 48.679688 8.425781 49.246094 8.425781 49.875 C 8.410156 50.191406 8.394531 50.515625 8.378906 50.839844 C 8.75 50.457031 9.148438 50.09375 9.582031 49.734375 C 9.929688 49.441406 10.589844 49.019531 10.6875 48.539062 Z M 14.714844 49.832031 C 14.835938 49.296875 15.097656 47.621094 14.023438 47.914062 C 13.0625 48.179688 12.175781 49.132812 11.851562 50.070312 C 11.421875 51.296875 12.078125 52.445312 13.445312 52.039062 C 14.144531 51.589844 14.542969 50.597656 14.714844 49.832031 Z M 17.359375 72.183594 C 17.480469 70.785156 17.238281 69.398438 16.300781 68.40625 C 15.789062 67.871094 15.308594 67.5625 14.855469 67.445312 C 14.941406 67.773438 15.042969 68.121094 15.164062 68.382812 C 15.433594 68.929688 15.324219 69.59375 14.757812 69.921875 C 14.261719 70.214844 13.488281 70.074219 13.21875 69.515625 C 13.03125 69.117188 12.890625 68.714844 12.769531 68.300781 C 12.199219 69.007812 11.769531 70.042969 11.5 71.171875 C 11.542969 71.183594 11.589844 71.207031 11.632812 71.230469 C 11.996094 71.464844 12.394531 71.628906 12.761719 71.855469 C 13.28125 72.183594 13.480469 72.851562 13.167969 73.402344 C 12.859375 73.914062 12.136719 74.132812 11.617188 73.808594 C 11.484375 73.71875 11.347656 73.648438 11.207031 73.574219 C 11.191406 74.882812 11.429688 76.085938 11.988281 76.789062 C 12.175781 77.039062 12.25 77.308594 12.234375 77.566406 C 12.902344 78.480469 13.640625 78.546875 14.324219 78.179688 C 14.234375 78.105469 14.15625 78.015625 14.097656 77.910156 C 13.878906 77.511719 13.640625 77.1875 13.480469 76.761719 C 13.265625 76.191406 13.714844 75.527344 14.269531 75.378906 C 14.902344 75.207031 15.445312 75.589844 15.652344 76.160156 C 15.644531 76.136719 15.644531 76.128906 15.644531 76.121094 C 15.675781 76.167969 15.726562 76.28125 15.734375 76.292969 C 15.773438 76.347656 15.8125 76.40625 15.847656 76.460938 C 15.871094 76.488281 15.886719 76.519531 15.902344 76.550781 C 16.089844 76.265625 16.253906 75.964844 16.390625 75.679688 C 16.570312 75.289062 16.75 74.859375 16.902344 74.394531 C 16.609375 74.320312 16.316406 74.242188 16.023438 74.167969 C 15.429688 74.019531 15.074219 73.363281 15.230469 72.777344 C 15.398438 72.175781 16.03125 71.847656 16.621094 71.996094 C 16.871094 72.058594 17.109375 72.117188 17.359375 72.183594 Z M 19.726562 63.226562 C 19.46875 62.746094 19.191406 62.289062 18.847656 61.867188 C 18.335938 61.214844 17.585938 60.757812 16.742188 60.371094 C 14.96875 59.660156 12.8125 59.695312 11.152344 60.671875 C 9.679688 61.539062 8.554688 63.625 7.78125 65.105469 C 7.417969 65.78125 6.230469 67.609375 6.261719 68.261719 C 6.269531 68.503906 6.277344 68.75 6.3125 68.96875 L 6.359375 69.308594 C 6.382812 69.410156 6.410156 69.496094 6.433594 69.59375 C 6.472656 69.816406 6.554688 69.929688 6.613281 70.066406 C 6.726562 70.207031 6.800781 70.367188 6.96875 70.515625 C 7.28125 70.847656 7.695312 71.15625 8.15625 71.457031 C 7.914062 67.359375 8.785156 63.121094 12.664062 61.464844 C 15.828125 60.101562 18.042969 61.207031 19.726562 63.226562 Z M 21.003906 80.636719 C 22.753906 76.910156 22.03125 72.800781 20.550781 69.140625 C 19.253906 66.277344 16.132812 59.863281 12.355469 64.445312 C 11.703125 65.242188 11.234375 66.113281 10.910156 67.015625 C 12.910156 64.421875 16.210938 64.296875 18.3125 67.347656 C 20.597656 70.644531 19.613281 75.363281 17.34375 78.40625 C 16.058594 80.132812 14.316406 80.9375 12.722656 80.554688 C 13.097656 81.1875 13.585938 81.71875 14.234375 82.027344 C 16.398438 83.078125 19.765625 83.28125 21.003906 80.636719 Z M 33.695312 73.890625 C 33.679688 72.695312 33.601562 71.441406 33.519531 70.148438 C 30.484375 69.277344 27.058594 68.261719 23.167969 67.359375 C 23.191406 67.445312 23.21875 67.535156 23.25 67.617188 C 24.070312 70.09375 24.496094 71.914062 24.582031 73.09375 C 24.601562 73.320312 24.609375 73.507812 24.609375 73.6875 C 26.171875 73.636719 27.765625 73.347656 29.417969 73.347656 C 29.9375 73.328125 30.476562 73.386719 30.96875 73.441406 C 31.449219 73.507812 31.914062 73.582031 32.378906 73.648438 C 32.835938 73.710938 33.273438 73.800781 33.695312 73.890625 Z M 34.289062 48.367188 C 34.023438 44.707031 34.699219 41.199219 36.066406 37.800781 C 31.484375 37.898438 26.789062 38.734375 22.519531 40.28125 C 21.371094 40.703125 20.140625 41.128906 19.132812 41.851562 C 17.035156 43.363281 18.832031 44.886719 20.613281 45.285156 C 22.378906 45.683594 24.175781 45.828125 25.941406 46.1875 C 28.757812 46.765625 31.5 47.652344 34.289062 48.367188 Z M 39.328125 37.863281 C 39.246094 37.863281 39.3125 37.855469 39.230469 37.847656 C 38.78125 37.824219 38.300781 37.816406 37.84375 37.800781 C 36.300781 41.3125 35.578125 44.96875 35.933594 48.78125 C 36.136719 48.824219 36.257812 48.878906 36.460938 48.914062 C 36.683594 48.960938 36.984375 49.003906 36.984375 49.042969 L 36.984375 49.035156 C 37.734375 45.277344 37.734375 41.371094 39.328125 37.863281 Z M 42.6875 38.328125 C 42.214844 38.222656 41.742188 38.132812 41.277344 38.066406 C 39.472656 41.523438 39.554688 45.554688 38.953125 49.328125 C 39.300781 49.386719 39.652344 49.441406 40.003906 49.492188 C 40.050781 45.617188 40.953125 41.800781 42.6875 38.328125 Z M 55.363281 48.050781 C 55.816406 48.214844 56.273438 48.390625 56.707031 48.605469 C 54.53125 43.746094 49.578125 40.304688 44.339844 38.75 C 44.324219 38.792969 44.308594 38.839844 44.289062 38.882812 C 42.550781 42.242188 41.703125 45.976562 41.6875 49.75 C 43.214844 49.980469 44.730469 50.246094 46.226562 50.644531 C 46.378906 49.960938 46.65625 49.328125 47.0625 48.847656 C 48.953125 46.601562 52.90625 47.171875 55.363281 48.050781 Z M 58.015625 73.078125 C 57.976562 71.066406 57.957031 68.976562 58.082031 66.933594 C 56.371094 66.152344 54.722656 65.40625 53.148438 64.695312 C 51.472656 63.988281 49.847656 63.355469 48.316406 62.730469 C 45.234375 61.5 42.410156 60.484375 39.90625 59.449219 C 38.097656 58.71875 36.445312 58.050781 34.925781 57.421875 C 34.445312 61.265625 34.84375 65.550781 35.144531 69.488281 C 35.925781 69.714844 36.691406 69.9375 37.421875 70.148438 C 41.605469 71.214844 45.003906 71.734375 47.542969 72.355469 C 50.089844 72.957031 51.816406 73.507812 52.882812 73.949219 C 53.949219 74.402344 54.386719 74.632812 54.355469 74.710938 C 54.28125 74.910156 52.464844 74.117188 47.375 73.140625 C 44.828125 72.621094 41.457031 72.191406 37.152344 71.15625 C 36.527344 70.988281 35.886719 70.816406 35.226562 70.628906 C 35.316406 71.90625 35.378906 73.125 35.386719 74.273438 C 36.058594 74.421875 36.714844 74.574219 37.34375 74.71875 C 38.089844 74.859375 38.804688 74.988281 39.488281 75.113281 C 40.945312 75.386719 42.296875 75.574219 43.5 75.875 C 44.703125 76.191406 45.8125 76.453125 46.789062 76.746094 C 47.765625 77.046875 48.644531 77.324219 49.433594 77.566406 C 50.996094 78.066406 52.191406 78.480469 53.078125 78.8125 L 53.132812 78.835938 C 53.679688 79.058594 54.109375 79.253906 54.4375 79.425781 C 54.636719 79.472656 54.824219 79.519531 55.023438 79.5625 C 55.355469 79.636719 55.703125 79.714844 56.054688 79.726562 L 56.316406 79.75 C 56.371094 79.757812 56.421875 79.765625 56.460938 79.757812 C 56.535156 79.75 56.609375 79.742188 56.6875 79.734375 C 56.714844 79.71875 56.777344 79.734375 56.785156 79.707031 L 56.785156 79.578125 C 56.785156 79.496094 56.785156 79.414062 56.777344 79.332031 C 56.789062 78.847656 56.835938 78.351562 56.902344 77.84375 C 56.964844 77.324219 57.03125 76.789062 57.152344 76.242188 C 57.257812 75.6875 57.371094 75.113281 57.558594 74.535156 C 57.683594 74.054688 57.84375 73.566406 58.015625 73.078125 Z M 58.347656 64.25 C 58.730469 61.550781 59.445312 58.914062 59.652344 56.203125 C 56.789062 56.015625 53.921875 55.863281 51.074219 55.550781 C 49.953125 55.429688 48.390625 55.421875 47.4375 54.746094 C 46.691406 54.226562 46.28125 53.332031 46.160156 52.371094 C 43.3125 51.574219 40.394531 51.417969 37.511719 50.824219 C 37.398438 50.800781 37.285156 50.769531 37.164062 50.746094 C 37.144531 50.832031 37.113281 50.914062 37.058594 50.996094 C 36.023438 52.589844 35.40625 54.4375 35.0625 56.429688 C 36.65625 57.050781 38.390625 57.734375 40.285156 58.480469 C 42.785156 59.488281 45.625 60.484375 48.722656 61.703125 C 50.261719 62.328125 51.890625 62.949219 53.589844 63.65625 C 55.054688 64.316406 56.589844 65.015625 58.171875 65.730469 C 58.21875 65.234375 58.277344 64.738281 58.347656 64.25 Z M 59.195312 54.480469 C 59.039062 54.242188 58.894531 53.984375 58.761719 53.730469 C 58.332031 53.730469 57.878906 53.460938 57.835938 52.917969 C 57.796875 52.492188 57.738281 52.0625 57.664062 51.648438 C 57.300781 51.085938 56.894531 50.605469 56.355469 50.320312 C 54.507812 49.351562 51.710938 48.515625 49.644531 49.167969 C 48.539062 49.523438 46.527344 52.835938 48.578125 53.40625 C 49.398438 53.640625 50.222656 53.777344 51.074219 53.859375 C 53.777344 54.113281 56.484375 54.300781 59.195312 54.480469 Z M 64.539062 52.332031 C 63.476562 51.214844 62.5625 49.972656 61.699219 48.628906 C 59.804688 45.675781 57.535156 43.03125 55.175781 40.445312 L 55.113281 40.523438 C 52.320312 38.09375 49.179688 36.59375 46.21875 35.601562 C 43.242188 34.617188 40.417969 34.121094 37.855469 33.917969 C 36.585938 33.796875 35.308594 33.722656 34.160156 33.65625 C 33.003906 33.601562 31.914062 33.535156 30.90625 33.570312 C 30.402344 33.570312 29.90625 33.578125 29.433594 33.578125 C 28.976562 33.632812 28.523438 33.675781 28.089844 33.722656 C 27.660156 33.78125 27.222656 33.789062 26.839844 33.871094 C 26.464844 33.96875 26.097656 34.03125 25.753906 34.136719 C 24.355469 34.546875 23.265625 35.230469 22.363281 35.804688 C 21.917969 36.097656 21.515625 36.367188 21.160156 36.636719 C 20.808594 36.894531 20.492188 37.125 20.222656 37.335938 C 18.589844 38.554688 17.410156 39.90625 16.050781 41.429688 C 15.75 41.792969 15.398438 42.152344 15.03125 42.519531 C 14.675781 42.890625 14.269531 43.273438 13.820312 43.625 C 12.941406 44.339844 11.941406 44.96875 11.003906 45.660156 C 10.988281 45.675781 10.972656 45.691406 10.949219 45.699219 C 11.355469 46.128906 11.730469 46.585938 11.996094 47.082031 C 12.414062 46.742188 12.875 46.472656 13.363281 46.34375 C 17.800781 45.144531 16.863281 52.09375 14.210938 53.558594 C 14.152344 53.589844 14.089844 53.617188 14.023438 53.632812 C 12.25 54.273438 10.46875 53.28125 10.070312 51.605469 C 8.167969 53.234375 7.703125 54.820312 7.109375 57.164062 C 6.707031 58.765625 6.492188 60.515625 6.390625 62.347656 C 6.382812 62.816406 6.367188 63.28125 6.359375 63.753906 C 6.351562 63.988281 6.34375 64.242188 6.34375 64.492188 C 6.53125 64.039062 6.71875 63.574219 6.898438 63.09375 C 7.171875 62.402344 7.433594 61.703125 7.808594 60.980469 C 8.003906 60.621094 8.207031 60.261719 8.546875 59.890625 L 8.808594 59.613281 C 8.890625 59.546875 8.972656 59.492188 9.054688 59.425781 L 9.539062 59.082031 C 10.84375 58.1875 12.332031 57.796875 13.714844 57.742188 C 15.105469 57.707031 16.40625 57.945312 17.546875 58.457031 C 18.671875 58.984375 19.703125 59.6875 20.386719 60.605469 C 21.0625 61.492188 21.53125 62.433594 21.832031 63.28125 C 22.152344 64.128906 22.378906 64.910156 22.601562 65.625 C 22.65625 65.796875 22.710938 65.949219 22.761719 66.113281 C 23.992188 66.398438 25.195312 66.660156 26.324219 66.96875 C 27.75 67.367188 29.125 67.722656 30.417969 68.105469 C 31.46875 68.414062 32.460938 68.707031 33.429688 68.984375 C 33.136719 64.964844 32.769531 60.664062 33.320312 56.75 C 33.28125 56.734375 33.234375 56.722656 33.199219 56.707031 C 31.222656 55.902344 29.507812 55.144531 28.050781 54.429688 C 25.121094 53.003906 23.363281 51.523438 22.3125 50.566406 C 21.335938 49.507812 20.957031 49.027344 21.019531 48.976562 C 21.078125 48.921875 21.566406 49.304688 22.601562 50.246094 C 23.722656 51.070312 25.480469 52.402344 28.398438 53.707031 C 29.832031 54.355469 31.507812 55.054688 33.460938 55.804688 C 33.820312 53.835938 34.453125 51.996094 35.472656 50.355469 C 33.476562 49.867188 31.5 49.289062 29.5 48.765625 C 26.226562 47.902344 22.617188 47.789062 19.417969 46.714844 C 14.046875 44.917969 16.328125 40.933594 20.53125 39.246094 C 27.75 36.328125 37.042969 34.75 44.582031 37.089844 C 51.492188 39.222656 58.023438 44.152344 59.339844 51.523438 C 59.367188 51.582031 59.40625 51.640625 59.433594 51.710938 C 61.539062 51.738281 63.214844 52.011719 64.539062 52.332031 Z M 73.011719 34.570312 C 73.058594 34.511719 73.058594 34.390625 72.878906 34.210938 C 72.789062 34.113281 72.667969 34.023438 72.546875 33.941406 C 72.457031 33.925781 72.359375 33.910156 72.269531 33.886719 C 71.894531 33.851562 71.527344 33.804688 71.15625 33.761719 C 70.421875 33.675781 69.699219 33.59375 68.984375 33.519531 C 67.550781 33.382812 66.144531 33.300781 64.785156 33.203125 C 59.316406 32.925781 54.410156 32.984375 50.050781 33.007812 C 48.390625 33.015625 46.804688 33.03125 45.300781 33.03125 C 45.828125 33.171875 46.363281 33.324219 46.910156 33.496094 C 48.539062 34.03125 50.238281 34.714844 51.921875 35.617188 C 53.0625 35.34375 54.167969 35.277344 55.214844 35.238281 C 56.429688 35.210938 57.566406 35.246094 58.640625 35.210938 C 60.820312 35.066406 62.800781 34.9375 64.613281 34.828125 C 65.523438 34.773438 66.394531 34.722656 67.210938 34.667969 C 67.625 34.648438 68.03125 34.625 68.414062 34.601562 L 68.707031 34.585938 C 68.84375 34.585938 68.925781 34.59375 69.023438 34.59375 C 69.210938 34.609375 69.398438 34.617188 69.578125 34.625 C 70.316406 34.667969 71 34.699219 71.636719 34.699219 C 71.960938 34.707031 72.269531 34.699219 72.546875 34.675781 C 72.691406 34.667969 72.832031 34.648438 72.929688 34.625 C 72.960938 34.625 72.996094 34.609375 73.011719 34.570312 Z M 77.6875 75.917969 C 77.121094 74.242188 76.371094 72.703125 75.433594 71.449219 C 74.304688 69.902344 72.863281 68.726562 71.332031 67.992188 C 69.796875 67.269531 68.171875 66.878906 66.730469 67.039062 C 65.289062 67.195312 64.003906 67.804688 63.003906 68.707031 C 61.988281 69.59375 61.222656 70.683594 60.617188 71.773438 C 60.023438 72.859375 59.546875 73.980469 59.226562 75.039062 C 59.03125 75.558594 58.910156 76.085938 58.789062 76.589844 C 58.648438 77.089844 58.566406 77.585938 58.488281 78.066406 C 58.398438 78.542969 58.332031 79.007812 58.292969 79.449219 C 58.257812 79.828125 58.21875 80.195312 58.179688 80.546875 C 58.160156 80.726562 58.144531 80.902344 58.121094 81.074219 C 58.121094 81.09375 58.121094 81.117188 58.113281 81.132812 L 58.046875 81.140625 L 57.910156 81.140625 L 57.648438 81.148438 C 57.300781 81.148438 56.964844 81.15625 56.632812 81.164062 C 56.476562 81.164062 56.332031 81.132812 56.183594 81.117188 L 55.867188 81.066406 C 55.4375 81.007812 55.070312 80.894531 54.71875 80.789062 C 53.304688 80.359375 52.28125 79.894531 51.464844 79.609375 C 51.351562 79.5625 51.246094 79.53125 51.132812 79.488281 C 50.515625 79.367188 49.820312 79.21875 49.03125 79.042969 C 48.234375 78.855469 47.339844 78.652344 46.355469 78.429688 C 45.371094 78.203125 44.289062 78.007812 43.109375 77.753906 C 41.921875 77.511719 40.628906 77.382812 39.230469 77.160156 C 38.496094 77.046875 37.730469 76.925781 36.925781 76.796875 C 36.15625 76.640625 35.355469 76.476562 34.527344 76.300781 C 33.722656 76.160156 32.875 75.925781 32.027344 75.835938 C 31.597656 75.777344 31.160156 75.707031 30.71875 75.648438 C 30.28125 75.609375 29.878906 75.566406 29.425781 75.582031 C 27.9375 75.574219 26.21875 75.933594 24.242188 75.957031 C 24.257812 76.476562 24.257812 76.992188 24.226562 77.503906 C 31.125 77.265625 36.796875 78.179688 41.359375 79.058594 C 42.550781 79.261719 43.65625 79.519531 44.703125 79.757812 C 45.753906 80 46.730469 80.230469 47.65625 80.441406 C 49.496094 80.886719 51.101562 81.269531 52.484375 81.605469 C 53.84375 81.929688 55.046875 82.199219 56.039062 82.492188 C 56.707031 82.695312 58.039062 83.457031 58.738281 83.117188 C 59.609375 82.6875 58.804688 80.800781 58.855469 79.945312 C 59.234375 73.65625 63.875 67.886719 70.625 69.488281 C 70.804688 69.53125 70.953125 69.605469 71.066406 69.699219 C 73.71875 70.996094 76.003906 73.238281 77.6875 75.917969 Z M 79.925781 36.953125 C 79.121094 36.441406 78.316406 35.96875 77.492188 35.578125 L 76.980469 35.316406 L 76.453125 35.097656 C 76.101562 34.953125 75.753906 34.8125 75.410156 34.667969 C 75.054688 34.5625 74.710938 34.449219 74.359375 34.34375 L 73.839844 34.1875 L 73.808594 34.179688 C 73.816406 34.1875 73.816406 34.1875 73.816406 34.195312 C 73.914062 34.445312 73.878906 34.765625 73.734375 35.023438 C 73.636719 35.253906 73.410156 35.398438 73.148438 35.464844 C 72.960938 35.511719 72.800781 35.53125 72.636719 35.554688 C 72.304688 35.585938 71.984375 35.601562 71.644531 35.617188 C 70.976562 35.632812 70.277344 35.617188 69.542969 35.59375 C 69.355469 35.585938 69.171875 35.578125 68.976562 35.570312 L 68.722656 35.570312 L 68.4375 35.59375 C 68.054688 35.621094 67.65625 35.652344 67.25 35.683594 C 66.4375 35.742188 65.582031 35.8125 64.679688 35.878906 C 62.863281 36.015625 60.863281 36.15625 58.675781 36.320312 C 57.566406 36.367188 56.414062 36.335938 55.242188 36.367188 C 54.640625 36.390625 54.03125 36.417969 53.425781 36.488281 C 54.152344 36.945312 54.882812 37.441406 55.597656 37.996094 C 59.757812 37.492188 63.890625 37.75 68.089844 37.703125 C 72.050781 37.660156 75.972656 37.164062 79.925781 36.953125 Z M 78.0625 65.21875 C 78.289062 65.078125 78.492188 65 78.679688 64.949219 C 77.492188 64.039062 76.679688 63.167969 76.035156 62.523438 C 75.859375 62.347656 75.695312 62.183594 75.550781 62.035156 C 75.3125 61.996094 75.078125 61.957031 74.847656 61.921875 C 74.320312 61.832031 73.808594 61.710938 73.289062 61.613281 C 72.269531 61.402344 71.261719 61.199219 70.277344 60.996094 C 69.789062 60.898438 69.324219 60.824219 68.796875 60.703125 L 68.363281 60.589844 C 68.152344 60.523438 67.941406 60.441406 67.746094 60.328125 C 67.355469 60.101562 67.054688 59.734375 66.941406 59.296875 C 66.828125 58.832031 66.835938 58.457031 66.835938 58.246094 L 66.820312 57.554688 C 66.804688 57.089844 66.777344 56.722656 66.695312 56.308594 C 66.65625 56.105469 66.609375 55.902344 66.558594 55.707031 L 66.476562 55.40625 L 66.453125 55.332031 L 66.402344 55.195312 L 66.289062 54.925781 L 66.183594 54.65625 L 66.121094 54.519531 L 66.019531 54.355469 L 65.582031 53.707031 C 65.542969 53.65625 65.515625 53.609375 65.476562 53.566406 C 65.460938 53.558594 65.453125 53.558594 65.441406 53.550781 C 64.921875 53.460938 64.34375 53.300781 63.6875 53.199219 C 63.019531 53.113281 62.289062 53.023438 61.480469 52.925781 C 61.027344 52.890625 60.5625 52.875 60.066406 52.867188 C 60.359375 53.347656 60.699219 53.796875 61.15625 54.199219 C 61.417969 54.429688 61.480469 54.714844 61.398438 54.964844 C 61.398438 54.96875 61.40625 54.976562 61.40625 54.984375 C 61.351562 57.910156 60.554688 60.628906 60.148438 63.5 C 59.863281 65.503906 59.75 67.554688 59.714844 69.605469 C 60.238281 68.78125 60.878906 67.96875 61.683594 67.226562 C 62.886719 66.082031 64.589844 65.203125 66.507812 64.980469 C 68.429688 64.738281 70.40625 65.210938 72.253906 66.054688 C 73.335938 66.554688 74.386719 67.242188 75.351562 68.082031 C 75.742188 67.625 76.09375 67.136719 76.445312 66.691406 C 76.996094 66.023438 77.542969 65.488281 78.0625 65.21875 Z M 71.140625 93.800781 C 77.117188 94.042969 79.378906 88.957031 78.21875 83.53125 C 77.207031 78.765625 74.464844 73.875 69.949219 71.652344 C 57.378906 68.773438 59.300781 93.320312 71.140625 93.800781 Z M 87.949219 67.632812 C 87.738281 67.210938 87.582031 66.722656 87.535156 66.152344 C 87.476562 65.445312 87.710938 64.582031 88.265625 63.917969 C 87.703125 63.835938 87.144531 63.761719 86.597656 63.671875 C 84.230469 63.328125 81.945312 62.996094 79.746094 62.679688 C 78.859375 62.542969 78.003906 62.410156 77.136719 62.28125 C 77.84375 62.84375 78.671875 63.515625 79.722656 64.160156 C 80.0625 64.355469 80.421875 64.527344 80.796875 64.730469 C 81.1875 64.898438 81.59375 65.0625 82.023438 65.242188 C 82.945312 65.59375 83.992188 65.949219 85.042969 66.414062 C 85.574219 66.640625 86.125 66.878906 86.695312 67.121094 C 87.101562 67.285156 87.53125 67.457031 87.949219 67.632812 Z M 92.707031 66.96875 C 92.714844 66.863281 92.667969 66.761719 92.660156 66.65625 L 92.675781 66.632812 L 92.683594 66.570312 L 92.667969 66.445312 C 92.660156 66.265625 92.601562 66.105469 92.546875 65.949219 C 92.414062 65.664062 92.246094 65.398438 92.015625 65.285156 C 91.910156 65.242188 91.753906 65.160156 91.714844 65.179688 C 91.683594 65.175781 91.699219 65.121094 91.496094 65.152344 L 91.113281 65.175781 C 90.683594 65.25 90.308594 65.355469 90.152344 65.496094 C 90 65.632812 89.902344 65.796875 89.867188 66.089844 C 89.804688 66.691406 90.175781 67.429688 90.574219 67.878906 C 90.871094 68.230469 91.21875 68.464844 91.503906 68.636719 C 91.851562 68.375 92.285156 68.058594 92.519531 67.691406 C 92.59375 67.585938 92.625 67.457031 92.660156 67.359375 C 92.660156 67.308594 92.660156 67.269531 92.675781 67.226562 C 92.683594 67.203125 92.691406 67.203125 92.699219 67.152344 Z M 95.890625 52.152344 C 98.507812 50.777344 96.378906 49.011719 94.757812 47.789062 C 93.96875 47.210938 93.195312 46.628906 92.421875 46.066406 C 91.65625 45.511719 90.894531 44.964844 90.152344 44.421875 C 88.65625 43.355469 87.175781 42.242188 85.726562 41.160156 C 84.5 40.265625 83.40625 39.378906 82.292969 38.5625 C 77.980469 38.628906 73.710938 39.335938 69.414062 39.378906 C 65.152344 39.425781 60.894531 39.117188 56.65625 39.558594 C 58.136719 41.175781 59.59375 42.820312 60.90625 44.570312 C 62.929688 47.253906 64.5 50.261719 67.085938 52.445312 C 67.722656 52.46875 68.355469 52.492188 68.96875 52.523438 C 69.84375 52.550781 70.660156 52.65625 71.480469 52.71875 C 72.292969 52.792969 73.082031 52.859375 73.855469 52.925781 C 74.628906 52.996094 75.378906 53.0625 76.109375 53.085938 C 76.835938 53.113281 77.558594 53.144531 78.257812 53.183594 C 78.964844 53.199219 79.664062 53.214844 80.339844 53.226562 C 81.699219 53.257812 82.992188 53.289062 84.222656 53.316406 C 85.441406 53.316406 86.597656 53.324219 87.6875 53.324219 C 88.234375 53.324219 88.769531 53.332031 89.289062 53.332031 C 89.804688 53.332031 90.285156 53.28125 90.769531 53.265625 C 92.429688 53.191406 94.410156 52.925781 95.890625 52.152344 Z M 96.253906 66.761719 C 96.269531 66.761719 96.359375 66.738281 96.34375 66.714844 C 96.335938 66.699219 96.328125 66.683594 96.320312 66.667969 L 96.304688 66.640625 C 96.289062 66.632812 96.3125 66.640625 96.199219 66.554688 C 95.863281 66.300781 95.53125 66.082031 95.230469 65.867188 C 95.09375 65.769531 94.976562 65.691406 94.847656 65.609375 C 94.894531 65.859375 94.929688 66.105469 94.90625 66.347656 L 94.902344 66.59375 L 94.902344 66.722656 L 94.894531 66.78125 L 94.878906 66.894531 L 94.878906 66.917969 L 94.871094 66.941406 C 94.839844 67.058594 94.808594 67.179688 94.789062 67.292969 L 94.765625 67.382812 C 94.914062 67.324219 95.058594 67.261719 95.195312 67.210938 C 95.464844 67.105469 95.71875 67 95.953125 66.894531 L 96.230469 66.769531 Z M 114.015625 85.835938 C 113.925781 85.800781 113.84375 85.761719 113.761719 85.730469 C 112.671875 85.898438 111.371094 86.121094 109.84375 86.40625 C 109.078125 86.574219 108.253906 86.746094 107.367188 86.933594 C 106.75 87.085938 106.105469 87.191406 105.441406 87.289062 C 107.472656 89 113.269531 88.632812 114.015625 85.835938 Z M 116.125 73.914062 C 116.148438 73.46875 116.117188 72.90625 115.929688 72.457031 C 115.871094 72.371094 115.8125 72.3125 115.5625 72.222656 C 115.316406 72.140625 114.960938 72.078125 114.554688 72.074219 C 113.746094 72.042969 112.738281 72.148438 111.617188 72.347656 C 111.054688 72.449219 110.460938 72.566406 109.835938 72.71875 C 109.527344 72.792969 109.207031 72.875 108.882812 72.957031 C 108.589844 73.039062 108.296875 73.125 107.996094 73.207031 C 107.988281 73.214844 107.988281 73.214844 107.988281 73.222656 C 107.996094 73.222656 108.003906 73.273438 108.050781 73.648438 C 108.160156 74.378906 108.199219 75.105469 108.246094 75.835938 C 108.449219 75.804688 108.648438 75.777344 108.859375 75.738281 C 110.132812 75.582031 111.257812 75.589844 112.40625 75.492188 C 113.527344 75.394531 114.617188 75.210938 115.375 74.695312 C 115.667969 74.5 115.910156 74.25 116.125 73.964844 C 116.125 73.941406 116.125 73.925781 116.125 73.914062 Z M 116.832031 60.140625 L 116.660156 59.988281 C 116.269531 59.660156 115.914062 59.289062 115.457031 59.027344 C 115.015625 58.742188 114.585938 58.441406 114.128906 58.148438 C 113.632812 57.894531 113.136719 57.621094 112.625 57.359375 C 110.597656 56.332031 108.3125 55.429688 105.945312 54.761719 C 104.765625 54.472656 103.398438 54.25 102.023438 53.875 C 101.324219 53.671875 100.617188 53.445312 99.882812 53.078125 C 99.703125 52.996094 99.515625 52.898438 99.328125 52.769531 C 99.144531 52.65625 98.957031 52.527344 98.769531 52.363281 C 98.730469 52.328125 98.6875 52.28125 98.640625 52.242188 C 98.5 52.394531 98.328125 52.523438 98.117188 52.609375 C 97.71875 52.808594 97.449219 52.890625 97.140625 53.03125 C 96.800781 53.160156 96.457031 53.296875 96.089844 53.429688 C 94.644531 54 92.902344 54.390625 90.894531 54.632812 C 90.398438 54.675781 89.875 54.753906 89.347656 54.769531 C 88.820312 54.78125 88.28125 54.796875 87.722656 54.8125 C 86.621094 54.84375 85.441406 54.871094 84.207031 54.910156 C 82.976562 54.933594 81.691406 54.917969 80.332031 54.925781 C 78.984375 54.925781 77.558594 54.917969 76.035156 54.867188 C 75.265625 54.859375 74.5 54.804688 73.71875 54.753906 C 72.945312 54.691406 72.148438 54.640625 71.335938 54.582031 C 70.53125 54.535156 69.699219 54.445312 68.871094 54.429688 L 68.398438 54.414062 L 68.308594 54.414062 L 68.226562 54.421875 C 68.195312 54.421875 68.152344 54.414062 68.195312 54.453125 C 68.21875 54.472656 68.234375 54.503906 68.25 54.527344 C 68.265625 54.558594 68.273438 54.574219 68.300781 54.65625 L 68.316406 54.707031 L 68.332031 54.730469 L 68.355469 54.820312 L 68.46875 55.1875 C 68.535156 55.429688 68.585938 55.675781 68.640625 55.933594 C 68.753906 56.429688 68.796875 56.992188 68.820312 57.472656 L 68.84375 58.203125 C 68.851562 58.464844 68.867188 58.578125 68.867188 58.578125 C 68.867188 58.601562 68.886719 58.621094 68.910156 58.628906 L 68.964844 58.644531 L 69.242188 58.710938 C 69.667969 58.808594 70.1875 58.894531 70.675781 58.992188 C 71.660156 59.179688 72.660156 59.375 73.675781 59.570312 C 74.183594 59.660156 74.695312 59.773438 75.214844 59.863281 C 75.734375 59.9375 76.25 60.011719 76.777344 60.089844 C 77.835938 60.246094 78.910156 60.402344 80.007812 60.5625 C 82.222656 60.867188 84.523438 61.183594 86.90625 61.515625 C 89.28125 61.882812 91.714844 62.140625 94.230469 62.417969 C 95.484375 62.542969 96.765625 62.542969 98.054688 62.621094 C 98.710938 62.640625 99.363281 62.695312 100.015625 62.6875 C 100.679688 62.648438 101.339844 62.621094 102.007812 62.582031 C 104.667969 62.492188 107.476562 62.191406 110.363281 61.929688 C 111.859375 61.777344 113.300781 61.734375 114.660156 61.484375 C 114.992188 61.410156 115.34375 61.355469 115.660156 61.265625 C 115.8125 61.222656 115.984375 61.183594 116.082031 61.140625 C 116.125 61.109375 116.203125 61.09375 116.238281 61.074219 C 116.269531 61.050781 116.300781 61.027344 116.335938 61.011719 C 116.433594 60.929688 116.523438 60.832031 116.667969 60.539062 C 116.71875 60.417969 116.78125 60.28125 116.832031 60.140625 Z M 117.667969 69.503906 C 117.585938 69.40625 117.480469 69.316406 117.34375 69.21875 C 117.1875 69.132812 117.007812 69.042969 116.789062 68.992188 C 116.359375 68.871094 115.871094 68.8125 115.390625 68.796875 C 114.429688 68.757812 113.496094 68.832031 112.664062 68.914062 C 111.394531 69.058594 110.25 69.464844 109.011719 69.796875 C 108.019531 70.066406 106.914062 70.101562 105.898438 70.277344 C 104.667969 70.492188 103.242188 70.800781 101.859375 71.578125 C 102.039062 71.785156 102.210938 71.996094 102.375 72.207031 L 102.835938 72.75 L 102.964844 72.90625 C 103.054688 73.019531 103.066406 73.046875 103.113281 73.109375 L 103.339844 73.425781 C 103.632812 73.835938 103.910156 74.25 104.195312 74.632812 C 104.480469 75.03125 104.789062 75.386719 105.082031 75.695312 C 105.15625 75.777344 105.222656 75.8125 105.300781 75.882812 L 105.398438 75.964844 C 105.417969 75.972656 105.441406 75.980469 105.464844 75.992188 C 105.511719 76.015625 105.539062 76.054688 105.613281 76.054688 C 105.683594 76.0625 105.714844 76.09375 105.824219 76.09375 C 105.878906 76.09375 105.9375 76.09375 105.996094 76.097656 C 105.945312 75.316406 105.914062 74.589844 105.816406 73.925781 C 105.824219 73.726562 105.613281 72.757812 105.480469 72.058594 C 105.21875 71.578125 105.824219 71.605469 106.117188 71.464844 C 106.472656 71.351562 106.816406 71.238281 107.164062 71.140625 L 107.554688 71.035156 L 107.816406 70.96875 C 107.996094 70.921875 108.175781 70.878906 108.351562 70.832031 C 108.703125 70.757812 109.039062 70.683594 109.378906 70.605469 C 110.046875 70.472656 110.6875 70.367188 111.304688 70.292969 C 112.535156 70.132812 113.660156 70.074219 114.722656 70.203125 C 115.246094 70.269531 115.765625 70.382812 116.277344 70.628906 C 116.613281 70.785156 116.960938 71.082031 117.199219 71.433594 C 117.367188 70.816406 117.515625 70.179688 117.667969 69.503906 Z M 117.734375 80.71875 C 117.71875 80.707031 117.695312 80.699219 117.683594 80.683594 L 117.480469 80.515625 C 117.410156 80.464844 117.335938 80.398438 117.3125 80.398438 C 117.238281 80.367188 117.207031 80.292969 117.089844 80.285156 C 116.992188 80.261719 116.886719 80.21875 116.847656 80.210938 C 116.796875 80.210938 116.652344 80.210938 116.546875 80.210938 C 116.074219 80.21875 115.554688 80.351562 114.933594 80.503906 C 114.773438 80.539062 114.617188 80.570312 114.457031 80.605469 C 114.316406 80.613281 114.171875 80.628906 114.03125 80.644531 C 113.746094 80.660156 113.472656 80.683594 113.203125 80.707031 C 112.753906 80.734375 112.332031 80.765625 111.925781 80.796875 C 111.421875 80.894531 110.902344 80.992188 110.332031 81.117188 C 109.957031 81.195312 109.566406 81.277344 109.160156 81.359375 C 108.734375 81.425781 108.28125 81.492188 107.839844 81.546875 C 106.953125 81.667969 106.019531 81.765625 105.097656 81.953125 C 104.628906 82.050781 104.171875 82.164062 103.722656 82.335938 C 103.234375 82.507812 102.917969 82.679688 102.542969 82.972656 C 102.503906 82.996094 102.476562 83.035156 102.4375 83.054688 C 102.667969 83.140625 102.933594 83.167969 103.226562 83.15625 C 103.773438 83.132812 104.328125 82.996094 104.902344 82.898438 C 105.179688 82.847656 105.515625 82.800781 105.773438 82.792969 C 106.042969 82.78125 106.304688 82.765625 106.5625 82.757812 C 107.070312 82.726562 107.5625 82.703125 108.019531 82.6875 C 108.941406 82.652344 109.761719 82.621094 110.484375 82.589844 C 111.210938 82.605469 111.84375 82.613281 112.390625 82.628906 C 112.550781 82.628906 112.691406 82.636719 112.84375 82.644531 C 113.453125 82.546875 114.179688 82.417969 115.023438 82.199219 C 115.585938 82.042969 116.210938 81.839844 116.804688 81.515625 C 117.171875 81.3125 117.503906 81.050781 117.734375 80.71875 Z M 119.964844 64.550781 C 119.785156 64.152344 119.589844 63.761719 119.402344 63.355469 C 119.148438 62.964844 118.890625 62.566406 118.628906 62.160156 C 118.582031 62.078125 118.53125 62.003906 118.480469 61.929688 C 118.28125 62.242188 118.019531 62.582031 117.667969 62.839844 C 117.539062 62.921875 117.410156 62.996094 117.285156 63.070312 C 117.15625 63.136719 117.042969 63.175781 116.921875 63.226562 C 116.675781 63.339844 116.480469 63.386719 116.269531 63.445312 C 115.855469 63.558594 115.464844 63.617188 115.066406 63.710938 C 113.480469 63.996094 111.972656 64.03125 110.574219 64.175781 C 107.6875 64.429688 104.894531 64.722656 102.089844 64.820312 C 101.398438 64.851562 100.707031 64.890625 100.023438 64.917969 C 99.339844 64.925781 98.664062 64.867188 97.996094 64.84375 C 97.710938 64.828125 97.425781 64.8125 97.140625 64.804688 C 97.191406 64.84375 97.253906 64.875 97.3125 64.910156 C 97.371094 64.949219 97.574219 65.085938 97.746094 65.203125 C 97.921875 65.324219 98.101562 65.445312 98.28125 65.574219 C 98.640625 65.820312 98.90625 66.089844 99.242188 66.367188 L 99.484375 66.578125 C 99.550781 66.65625 99.722656 66.722656 99.574219 66.796875 C 99.414062 66.957031 99.25 67.113281 99.09375 67.269531 C 98.933594 67.429688 98.769531 67.585938 98.613281 67.738281 C 98.429688 67.894531 98.230469 68.042969 98.035156 68.195312 C 97.839844 68.351562 97.589844 68.472656 97.363281 68.617188 C 97.230469 68.699219 97.167969 68.726562 97.101562 68.765625 L 96.890625 68.871094 C 96.832031 68.902344 96.765625 68.921875 96.703125 68.953125 C 96.882812 68.96875 97.058594 68.96875 97.246094 68.984375 C 97.710938 69.007812 98.207031 69.140625 98.703125 69.238281 C 98.964844 69.335938 99.242188 69.417969 99.5 69.539062 C 99.722656 69.675781 99.972656 69.796875 100.183594 69.945312 C 101.078125 69.382812 101.984375 68.992188 102.828125 68.742188 C 103.855469 68.433594 104.789062 68.292969 105.613281 68.210938 C 107.980469 67.984375 110.054688 67.226562 112.390625 66.851562 C 113.277344 66.707031 114.277344 66.570312 115.449219 66.578125 C 116.042969 66.59375 116.675781 66.632812 117.390625 66.828125 C 117.6875 66.902344 118.003906 67.03125 118.328125 67.195312 C 118.335938 67.179688 118.34375 67.15625 118.351562 67.144531 C 118.53125 66.753906 118.75 66.414062 118.960938 66.089844 C 119.355469 65.511719 119.710938 65.039062 119.964844 64.550781 Z M 121.324219 82.613281 C 121.5 82.382812 121.648438 82.082031 121.777344 81.726562 C 121.296875 81.800781 120.769531 81.871094 120.257812 81.773438 C 119.980469 81.742188 119.757812 81.667969 119.515625 81.605469 C 119.304688 81.523438 119.078125 81.457031 118.898438 81.375 C 118.839844 81.34375 118.785156 81.320312 118.726562 81.296875 C 118.636719 81.441406 118.539062 81.570312 118.425781 81.675781 C 118.085938 82.050781 117.695312 82.289062 117.328125 82.492188 C 116.59375 82.878906 115.894531 83.070312 115.269531 83.207031 C 114.015625 83.476562 113.039062 83.515625 112.292969 83.539062 C 111.769531 83.539062 111.371094 83.523438 111.0625 83.5 C 110.882812 83.507812 110.710938 83.515625 110.519531 83.523438 C 109.800781 83.582031 108.988281 83.652344 108.078125 83.726562 C 107.628906 83.757812 107.148438 83.792969 106.644531 83.832031 C 106.390625 83.847656 106.132812 83.867188 105.863281 83.882812 C 105.585938 83.898438 105.382812 83.9375 105.105469 83.988281 C 104.570312 84.085938 103.976562 84.238281 103.277344 84.273438 C 102.933594 84.289062 102.550781 84.28125 102.152344 84.152344 C 101.949219 84.101562 101.738281 84.003906 101.550781 83.875 C 101.460938 83.957031 101.363281 84.046875 101.25 84.140625 C 100.738281 84.574219 100.023438 85.039062 99.332031 85.25 C 97.921875 85.769531 96.417969 85.851562 94.945312 85.84375 C 94.210938 85.835938 93.464844 85.808594 92.730469 85.785156 C 92 85.761719 91.257812 85.769531 90.460938 85.777344 C 88.890625 85.808594 87.214844 85.84375 85.433594 85.785156 C 83.945312 85.730469 82.359375 85.605469 80.722656 85.226562 C 80.746094 85.722656 80.746094 86.21875 80.722656 86.714844 C 82.332031 86.695312 83.15625 86.671875 84.253906 86.648438 C 85.546875 86.617188 86.90625 86.582031 87.957031 86.550781 C 90.070312 86.535156 91.722656 86.511719 92.984375 86.59375 C 95.480469 86.777344 96.433594 86.949219 96.433594 87.105469 C 96.425781 87.265625 95.417969 87.371094 92.925781 87.390625 C 91.675781 87.414062 89.992188 87.519531 87.898438 87.59375 C 86.84375 87.640625 85.582031 87.699219 84.289062 87.761719 C 83.164062 87.78125 82.316406 87.8125 80.640625 87.84375 C 80.585938 88.257812 80.511719 88.65625 80.429688 89.050781 C 83.847656 89.234375 87.019531 89.398438 89.917969 89.546875 C 91.570312 89.691406 93.097656 89.847656 94.511719 89.871094 C 95.207031 89.886719 95.890625 89.871094 96.441406 89.765625 C 96.703125 89.707031 96.929688 89.65625 97.042969 89.546875 C 97.109375 89.527344 97.183594 89.453125 97.261719 89.367188 C 97.34375 89.308594 97.425781 89.203125 97.507812 89.089844 C 97.851562 88.660156 98.191406 88.070312 98.695312 87.480469 L 99.132812 87.054688 C 99.289062 86.917969 99.492188 86.796875 99.679688 86.6875 C 99.875 86.542969 100.015625 86.519531 100.191406 86.445312 L 100.671875 86.257812 C 101.941406 85.84375 103.097656 85.722656 104.148438 85.597656 C 105.210938 85.46875 106.164062 85.386719 107.011719 85.226562 C 107.9375 85.085938 108.785156 84.957031 109.582031 84.839844 C 110.242188 84.753906 118.417969 83.875 118.417969 84.851562 C 118.417969 85.011719 117.808594 85.175781 116.433594 85.355469 C 116.40625 85.355469 116.375 85.363281 116.335938 85.363281 C 116.335938 85.445312 116.328125 85.527344 116.320312 85.609375 C 116.8125 85.703125 117.328125 85.738281 117.878906 85.65625 C 118.035156 85.65625 118.183594 85.597656 118.351562 85.550781 L 118.589844 85.484375 C 118.664062 85.460938 118.710938 85.417969 118.777344 85.386719 C 119.027344 85.28125 119.253906 85.003906 119.574219 84.671875 C 119.664062 84.566406 119.644531 84.582031 119.71875 84.347656 L 119.824219 83.996094 C 119.867188 83.859375 119.949219 83.664062 120.054688 83.5 C 120.199219 83.109375 120.597656 82.898438 120.980469 82.785156 C 121.234375 82.703125 121.175781 82.71875 121.234375 82.695312 C 121.273438 82.671875 121.304688 82.644531 121.324219 82.613281 Z M 121.949219 75.609375 C 122.003906 75.574219 122.039062 75.542969 122.085938 75.511719 C 121.972656 74.09375 121.769531 72.582031 121.582031 70.9375 C 121.410156 69.742188 121.230469 68.503906 120.90625 67.257812 C 120.882812 67.292969 120.851562 67.332031 120.828125 67.359375 C 120.65625 67.625 120.5 67.871094 120.386719 68.113281 C 120.335938 68.230469 120.273438 68.351562 120.242188 68.472656 C 120.207031 68.59375 120.160156 68.699219 120.125 68.878906 C 119.824219 70.140625 119.554688 71.515625 119.125 72.851562 C 118.847656 73.53125 118.679688 74.152344 118.246094 74.859375 C 117.832031 75.535156 117.261719 76.136719 116.601562 76.566406 C 115.246094 77.4375 113.8125 77.578125 112.578125 77.699219 C 111.355469 77.789062 110.152344 77.789062 109.167969 77.910156 C 108.09375 78.046875 106.988281 78.332031 105.613281 78.242188 C 105.457031 78.242188 105.230469 78.171875 105.035156 78.128906 C 104.832031 78.097656 104.636719 77.992188 104.449219 77.886719 L 104.164062 77.722656 L 103.960938 77.558594 C 103.835938 77.453125 103.691406 77.332031 103.578125 77.21875 C 103.148438 76.777344 102.789062 76.324219 102.480469 75.890625 C 102.164062 75.453125 101.886719 75.023438 101.609375 74.617188 L 101.40625 74.328125 C 101.378906 74.289062 101.339844 74.222656 101.339844 74.222656 L 101.234375 74.101562 C 101.078125 73.90625 100.917969 73.710938 100.761719 73.515625 C 100.152344 72.742188 99.613281 72.058594 99.039062 71.628906 C 98.898438 71.515625 98.746094 71.457031 98.605469 71.359375 C 98.453125 71.289062 98.296875 71.246094 98.152344 71.175781 C 97.777344 71.101562 97.417969 70.980469 97.019531 70.960938 C 94.960938 70.703125 93.007812 70.945312 90.925781 70.5625 C 90.527344 70.472656 90.191406 70.320312 89.828125 70.207031 C 89.136719 69.945312 88.414062 69.75 87.816406 69.457031 C 87.191406 69.179688 86.589844 68.910156 86.011719 68.652344 C 85.457031 68.382812 84.914062 68.128906 84.390625 67.878906 C 83.351562 67.359375 82.398438 66.984375 81.511719 66.585938 C 81.046875 66.363281 80.601562 66.144531 80.171875 65.933594 C 80 65.828125 79.828125 65.722656 79.65625 65.617188 C 79.648438 65.632812 79.648438 65.648438 79.640625 65.664062 C 79.527344 65.875 79.324219 66.089844 79.09375 66.445312 C 78.835938 66.769531 78.558594 67.226562 78.152344 67.886719 C 77.851562 68.359375 77.507812 69.015625 76.90625 69.714844 C 77.003906 69.839844 77.109375 69.960938 77.199219 70.089844 C 78.542969 71.875 79.566406 74.011719 80.210938 76.308594 C 80.828125 78.421875 81.152344 80.390625 81.210938 83.027344 C 82.636719 83.351562 84.101562 83.476562 85.523438 83.539062 C 87.214844 83.597656 88.851562 83.574219 90.4375 83.566406 C 91.226562 83.558594 92.023438 83.558594 92.804688 83.597656 C 93.5625 83.628906 94.292969 83.671875 94.976562 83.679688 C 96.359375 83.71875 97.613281 83.644531 98.628906 83.289062 C 99.175781 83.140625 99.527344 82.898438 99.949219 82.570312 C 100.363281 82.246094 100.777344 81.808594 101.324219 81.398438 C 101.859375 81 102.550781 80.667969 103.089844 80.511719 C 103.652344 80.316406 104.226562 80.195312 104.757812 80.109375 C 105.042969 80.058594 105.328125 80.027344 105.605469 79.992188 C 106.050781 79.757812 107.140625 79.527344 109.140625 79.292969 C 109.835938 79.230469 110.597656 79.074219 111.484375 78.949219 C 111.925781 78.878906 112.398438 78.8125 112.902344 78.742188 C 113.152344 78.707031 113.40625 78.667969 113.671875 78.640625 C 113.804688 78.617188 113.941406 78.601562 114.074219 78.585938 C 114.195312 78.546875 114.316406 78.511719 114.441406 78.480469 C 114.9375 78.339844 115.617188 78.105469 116.433594 78.054688 C 116.660156 78.046875 116.894531 78.046875 117.125 78.039062 C 117.410156 78.097656 117.621094 78.164062 117.855469 78.234375 C 118.078125 78.277344 118.320312 78.445312 118.554688 78.570312 C 118.679688 78.652344 118.742188 78.699219 118.816406 78.757812 L 119.035156 78.933594 C 119.140625 79 119.253906 79.066406 119.363281 79.140625 C 119.363281 79.15625 119.492188 79.203125 119.621094 79.253906 C 119.523438 79.082031 119.449219 78.847656 119.410156 78.625 L 119.386719 78.398438 L 119.378906 78.339844 C 119.378906 78.292969 119.378906 78.269531 119.378906 78.242188 L 119.386719 78.054688 C 119.425781 77.550781 119.71875 77.136719 119.972656 76.886719 C 120.242188 76.625 120.507812 76.460938 120.746094 76.308594 C 121.230469 76.015625 121.632812 75.804688 121.949219 75.609375 Z M 122.183594 79.269531 C 122.226562 78.453125 122.21875 77.570312 122.167969 76.640625 C 121.925781 76.851562 121.679688 77.0625 121.417969 77.265625 C 121.003906 77.578125 120.636719 77.949219 120.648438 78.164062 C 120.648438 78.179688 120.648438 78.195312 120.648438 78.21875 L 120.640625 78.234375 L 120.648438 78.285156 L 120.664062 78.519531 C 120.695312 78.578125 120.6875 78.625 120.730469 78.707031 C 120.800781 78.847656 120.90625 78.984375 121.054688 79.089844 C 121.289062 79.238281 121.566406 79.332031 121.835938 79.382812 C 121.859375 79.375 121.875 79.375 121.898438 79.367188 C 121.988281 79.339844 122.085938 79.308594 122.183594 79.269531 Z M 123.949219 75.527344 C 124.023438 77.046875 124.03125 78.480469 123.871094 79.847656 C 123.699219 81.207031 123.421875 82.53125 122.484375 83.671875 C 122.394531 83.746094 122.324219 83.832031 122.242188 83.898438 C 122.152344 83.957031 122.0625 84.027344 121.957031 84.0625 C 121.792969 84.152344 121.492188 84.230469 121.492188 84.230469 C 121.394531 84.242188 121.3125 84.265625 121.28125 84.347656 C 121.242188 84.394531 121.183594 84.558594 121.085938 84.824219 C 121.046875 84.929688 120.996094 85.085938 120.882812 85.25 C 120.839844 85.328125 120.785156 85.402344 120.738281 85.484375 L 120.558594 85.671875 C 120.378906 85.835938 120.265625 85.972656 120.035156 86.144531 C 119.839844 86.308594 119.636719 86.46875 119.371094 86.566406 C 119.246094 86.617188 119.125 86.6875 119.003906 86.722656 C 118.890625 86.746094 118.777344 86.769531 118.664062 86.792969 C 118.449219 86.835938 118.238281 86.898438 118.019531 86.890625 C 117.59375 86.902344 117.1875 86.917969 116.816406 86.835938 C 116.554688 86.796875 116.320312 86.738281 116.097656 86.671875 C 114.464844 91.179688 105.261719 91.765625 102.933594 87.707031 C 102.382812 87.8125 101.84375 87.949219 101.324219 88.136719 L 100.980469 88.285156 C 100.867188 88.332031 100.707031 88.375 100.671875 88.4375 C 100.601562 88.496094 100.527344 88.519531 100.453125 88.585938 C 100.386719 88.667969 100.308594 88.746094 100.226562 88.820312 C 99.910156 89.195312 99.617188 89.738281 99.152344 90.367188 C 99.039062 90.527344 98.921875 90.683594 98.746094 90.847656 C 98.589844 91.015625 98.425781 91.171875 98.183594 91.316406 C 97.746094 91.628906 97.273438 91.742188 96.859375 91.839844 C 96.035156 92.011719 95.269531 92.027344 94.488281 92.035156 C 92.941406 92.027344 91.359375 91.878906 89.753906 91.757812 C 86.679688 91.609375 83.320312 91.449219 79.671875 91.269531 C 77.710938 95.320312 73.140625 97.214844 68.511719 95.558594 C 63.972656 93.945312 60.578125 89.457031 59.34375 84.648438 C 59.339844 84.648438 59.332031 84.648438 59.324219 84.648438 C 59.179688 84.605469 59.007812 84.542969 58.804688 84.46875 C 58.585938 84.410156 58.339844 84.335938 58.046875 84.242188 C 57.46875 84.070312 56.707031 83.898438 55.746094 83.726562 C 54.753906 83.566406 53.566406 83.386719 52.164062 83.167969 C 50.734375 82.921875 49.132812 82.628906 47.277344 82.277344 C 46.355469 82.101562 45.363281 81.90625 44.316406 81.710938 C 43.273438 81.5 42.167969 81.285156 40.988281 81.109375 C 36.375 80.335938 30.703125 79.480469 23.902344 79.773438 C 23.339844 82.148438 22.003906 84.070312 19.433594 84.703125 C 13.863281 86.0625 10.628906 82.621094 9.230469 77.640625 C 8.914062 76.519531 8.921875 74.957031 8.191406 74.09375 C 7.441406 73.207031 6.140625 72.90625 5.328125 72.066406 C 5.089844 71.839844 4.878906 71.515625 4.675781 71.222656 C 4.488281 70.871094 4.316406 70.507812 4.261719 70.1875 C 4.15625 69.855469 4.113281 69.546875 4.082031 69.246094 C 4.039062 68.9375 4.03125 68.652344 4.015625 68.367188 C 3.96875 67.234375 4.039062 66.179688 4.082031 65.191406 C 4.113281 64.679688 4.121094 64.234375 4.136719 63.746094 C 4.148438 63.234375 4.164062 62.738281 4.179688 62.242188 C 4.308594 60.269531 4.554688 58.390625 5.019531 56.632812 C 5.449219 54.902344 6.019531 53.394531 6.195312 51.964844 C 6.285156 51.605469 6.292969 51.25 6.3125 50.898438 C 6.34375 50.539062 6.367188 50.175781 6.390625 49.824219 C 6.402344 48.980469 6.605469 48.125 6.945312 47.367188 C 7.277344 46.59375 7.785156 45.960938 8.304688 45.445312 C 8.832031 44.917969 9.378906 44.503906 9.914062 44.144531 C 10.972656 43.414062 11.941406 42.851562 12.761719 42.25 C 13.167969 41.957031 13.527344 41.640625 13.878906 41.304688 C 14.234375 40.980469 14.578125 40.671875 14.886719 40.335938 C 16.164062 39.050781 17.222656 37.855469 18.230469 36.96875 C 18.484375 36.742188 18.710938 36.523438 18.953125 36.335938 C 19.855469 35.652344 20.597656 34.722656 21.550781 34.121094 C 22.160156 33.746094 22.851562 33.632812 23.511719 33.375 C 25.8125 32.496094 27.855469 31.890625 30.34375 31.730469 C 32.65625 31.257812 35.4375 31.21875 38.621094 31.289062 C 41.890625 31.371094 45.664062 31.234375 50.019531 31.136719 C 54.378906 31.03125 59.316406 30.898438 64.882812 31.121094 C 66.273438 31.210938 67.707031 31.28125 69.171875 31.402344 C 69.910156 31.476562 70.652344 31.558594 71.40625 31.632812 C 71.78125 31.679688 72.164062 31.714844 72.539062 31.753906 C 72.9375 31.828125 73.34375 31.902344 73.75 31.972656 L 74.359375 32.085938 L 74.953125 32.265625 C 75.34375 32.378906 75.746094 32.496094 76.148438 32.617188 C 76.53125 32.777344 76.917969 32.933594 77.304688 33.089844 L 77.890625 33.332031 L 78.453125 33.609375 C 79.992188 34.332031 81.421875 35.269531 82.871094 36.238281 C 84.289062 37.230469 85.6875 38.371094 87.085938 39.386719 C 88.5 40.429688 89.933594 41.507812 91.472656 42.601562 C 92.242188 43.160156 93.015625 43.714844 93.789062 44.277344 C 94.554688 44.84375 95.328125 45.40625 96.117188 45.984375 C 96.914062 46.585938 97.726562 47.21875 98.492188 47.976562 C 99.273438 48.742188 99.769531 49.867188 100.632812 50.515625 C 102.234375 51.703125 104.628906 52.039062 106.492188 52.574219 C 109.125 53.332031 111.460938 54.28125 113.640625 55.390625 C 114.171875 55.675781 114.699219 55.960938 115.21875 56.242188 C 115.734375 56.5625 116.230469 56.917969 116.726562 57.246094 C 117.246094 57.554688 117.667969 57.992188 118.109375 58.375 C 118.328125 58.570312 118.546875 58.765625 118.765625 58.960938 C 118.96875 59.164062 119.140625 59.398438 119.328125 59.605469 C 119.515625 59.832031 119.695312 60.050781 119.882812 60.261719 C 120.070312 60.476562 120.242188 60.695312 120.378906 60.9375 C 120.679688 61.410156 120.964844 61.875 121.257812 62.34375 C 121.710938 63.320312 122.183594 64.257812 122.453125 65.226562 C 123.097656 67.136719 123.339844 69.007812 123.542969 70.734375 C 123.699219 72.402344 123.882812 74.011719 123.949219 75.527344"></path><path fill="inherit" d="M 118.507812 64.566406 C 118.5625 64.640625 118.371094 64.835938 117.976562 65.136719 C 117.777344 65.308594 117.503906 65.414062 117.1875 65.566406 C 116.863281 65.730469 116.488281 65.84375 116.066406 65.964844 C 115.226562 66.210938 114.203125 66.367188 113.082031 66.480469 C 112.511719 66.535156 111.933594 66.578125 111.332031 66.617188 C 110.722656 66.660156 110.101562 66.691406 109.515625 66.773438 C 108.296875 66.957031 107.078125 67.234375 105.960938 67.390625 C 104.832031 67.546875 103.78125 67.601562 102.886719 67.480469 C 101.992188 67.367188 101.292969 67.105469 100.867188 66.769531 C 100.46875 66.46875 100.339844 66.226562 100.386719 66.160156 C 100.429688 66.074219 100.691406 66.203125 101.121094 66.347656 C 101.511719 66.480469 102.160156 66.59375 102.949219 66.585938 C 103.734375 66.578125 104.691406 66.453125 105.765625 66.234375 C 106.839844 66.023438 108.011719 65.722656 109.335938 65.519531 C 110.023438 65.421875 110.65625 65.40625 111.257812 65.378906 C 111.859375 65.355469 112.445312 65.339844 113 65.316406 C 114.097656 65.273438 115.074219 65.210938 115.878906 65.09375 C 117.503906 64.882812 118.386719 64.402344 118.507812 64.566406"></path><path fill="inherit" d="M 98.019531 81.007812 C 98.109375 80.960938 98.167969 80.90625 98.167969 80.90625 C 98.125 80.773438 97.914062 80.546875 97.710938 80.375 L 97.679688 80.351562 C 97.449219 80.117188 97.011719 79.960938 96.597656 79.871094 C 96.175781 79.78125 95.757812 79.726562 95.351562 79.691406 C 94.546875 79.632812 93.832031 79.621094 93.238281 79.609375 C 92.929688 79.609375 92.660156 79.601562 92.421875 79.585938 C 91.160156 79.636719 89.902344 79.660156 88.671875 79.878906 C 88.394531 79.921875 88.101562 79.96875 87.792969 80.015625 C 87.175781 80.117188 85.027344 80.464844 84.832031 81.195312 C 84.816406 81.253906 84.816406 81.3125 84.824219 81.375 C 86.875 81.808594 89.054688 81.367188 91.128906 81.398438 L 91.578125 81.40625 L 91.625 81.40625 C 93.15625 81.507812 94.765625 81.515625 96.171875 81.398438 C 96.859375 81.335938 97.582031 81.222656 98.019531 81.007812 Z M 99.160156 80.464844 C 99.289062 80.675781 99.328125 81.109375 99.160156 81.410156 C 98.996094 81.734375 98.769531 81.863281 98.574219 81.988281 C 97.792969 82.402344 97.066406 82.484375 96.296875 82.589844 C 94.757812 82.757812 93.210938 82.78125 91.480469 82.664062 L 91.105469 82.660156 C 88.964844 82.621094 86.777344 82.878906 84.78125 82.433594 C 84.09375 82.28125 83.734375 82.074219 83.59375 81.832031 C 83.222656 81.1875 84.480469 80.324219 85.433594 79.847656 C 88.371094 78.40625 92.195312 78.886719 95.382812 78.855469 C 95.808594 78.855469 96.277344 78.871094 96.777344 78.941406 C 97.261719 79.03125 97.808594 79.136719 98.355469 79.5625 L 98.371094 79.578125 C 98.636719 79.796875 98.933594 80.007812 99.160156 80.464844"></path><path fill="inherit" d="M 71.503906 73.867188 C 75.175781 75.46875 76.703125 79.15625 76.140625 83.070312 C 75.679688 86.234375 73.890625 90.203125 70.390625 90.855469 C 61.140625 92.597656 59.855469 70.808594 70.917969 73.671875 C 71.015625 73.6875 71.113281 73.703125 71.222656 73.746094 C 71.332031 73.777344 71.421875 73.824219 71.503906 73.867188 Z M 68.632812 87.4375 C 68.640625 87.429688 68.640625 87.4375 68.640625 87.4375 C 68.640625 87.445312 68.480469 87.582031 68.480469 87.582031 C 68.4375 87.625 68.390625 87.675781 68.355469 87.730469 C 68.265625 87.828125 68.179688 87.933594 68.085938 88.03125 C 68.085938 88.03125 68.078125 88.039062 68.070312 88.039062 C 69.058594 88.8125 70.234375 89.046875 71.421875 87.933594 C 71.613281 87.753906 71.804688 87.550781 71.976562 87.339844 C 71.945312 87.316406 71.910156 87.308594 71.878906 87.28125 C 71.40625 86.8125 70.992188 86.46875 70.351562 86.207031 C 69.789062 85.964844 69.667969 85.136719 69.949219 84.65625 C 70.285156 84.078125 70.925781 84.019531 71.488281 84.253906 C 72.109375 84.523438 72.667969 84.941406 73.171875 85.402344 C 73.734375 84.148438 74.050781 82.734375 74.027344 81.367188 C 73.269531 81.585938 72.488281 81.71875 71.71875 81.929688 C 70.316406 82.320312 69.722656 80.140625 71.121094 79.757812 C 71.953125 79.53125 72.808594 79.390625 73.628906 79.136719 C 73.636719 79.128906 73.636719 79.128906 73.644531 79.128906 C 73.164062 77.722656 72.195312 76.542969 70.625 75.917969 C 70.375 75.851562 70.144531 75.796875 69.917969 75.761719 C 69.917969 76.519531 69.894531 77.273438 69.753906 78.015625 C 69.640625 78.617188 68.917969 78.953125 68.371094 78.804688 C 67.738281 78.632812 67.46875 78.015625 67.582031 77.414062 C 67.609375 77.242188 67.640625 76.925781 67.65625 76.640625 C 67.664062 76.453125 67.65625 76.257812 67.664062 76.070312 C 66.609375 76.617188 65.941406 77.722656 65.589844 79.035156 C 65.730469 79.089844 65.859375 79.171875 65.957031 79.300781 C 66.515625 79.992188 67.085938 80.667969 67.707031 81.296875 C 68.738281 82.335938 67.144531 83.929688 66.113281 82.890625 C 65.832031 82.605469 65.558594 82.304688 65.289062 81.996094 C 65.335938 82.867188 65.46875 83.71875 65.703125 84.441406 C 65.882812 85.003906 66.191406 85.679688 66.597656 86.324219 C 66.875 86.03125 67.128906 85.753906 67.476562 85.507812 C 67.972656 85.152344 68.722656 85.417969 69.015625 85.910156 C 69.339844 86.460938 69.121094 87.070312 68.640625 87.429688 C 68.640625 87.429688 68.640625 87.429688 68.632812 87.4375"></path><path fill="inherit" d="M 42.246094 55.640625 C 43.335938 55.554688 43.328125 57.246094 42.246094 57.335938 C 40.277344 57.488281 38.335938 56.742188 36.746094 55.625 C 35.863281 55 36.707031 53.535156 37.601562 54.160156 C 38.96875 55.128906 40.546875 55.773438 42.246094 55.640625"></path><path fill="inherit" d="M 15.644531 76.121094 C 15.636719 76.105469 15.636719 76.105469 15.636719 76.105469 C 15.636719 76.105469 15.644531 76.105469 15.644531 76.121094"></path></g></svg>
```

## assets/illustrations/sneaker-red.svg

```svg
<?xml version="1.0"?><svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" contentScriptType="text/ecmascript" fill="#ff2727" width="122.5" zoomAndPan="magnify" contentStyleType="text/css" viewBox="3.9 27.3 122.5 72.0" height="72" preserveAspectRatio="xMidYMid meet" version="1"><g id="change1_1"><path fill="inherit" d="M 23.695312 81.824219 C 23.90625 81.832031 24.128906 81.835938 24.34375 81.84375 C 24.25 73 18.71875 66.78125 9.980469 65.078125 C 9.359375 68.351562 8.601562 71.585938 7.601562 74.808594 C 6.890625 77.105469 6.484375 79.457031 6.277344 81.832031 C 11.726562 81.582031 17.171875 81.609375 22.613281 81.78125 C 22.515625 78.675781 21.554688 76.152344 20.367188 74.34375 C 19.046875 72.285156 17.539062 71.035156 16.363281 70.167969 C 15.171875 69.3125 14.269531 68.820312 13.699219 68.496094 C 13.117188 68.183594 12.882812 68.003906 12.910156 67.929688 C 12.941406 67.859375 13.226562 67.910156 13.871094 68.109375 C 14.507812 68.324219 15.484375 68.726562 16.792969 69.539062 C 18.074219 70.363281 19.730469 71.621094 21.199219 73.800781 C 22.519531 75.722656 23.585938 78.484375 23.695312 81.824219 Z M 54.5 40.734375 C 53.734375 37.625 53.019531 34.1875 51.246094 31.535156 C 49.660156 29.152344 47.851562 30.769531 45.804688 31.683594 C 44.035156 32.46875 41.894531 33.164062 40.953125 34.953125 C 41.339844 35.074219 41.722656 35.214844 42.097656 35.367188 C 42.179688 35.164062 42.289062 34.988281 42.402344 34.835938 C 42.695312 34.464844 43.027344 34.214844 43.339844 33.984375 C 43.96875 33.558594 44.578125 33.277344 45.121094 33.042969 C 46.214844 32.59375 47.101562 32.363281 47.785156 32.214844 C 49.152344 31.933594 49.722656 32.042969 49.730469 32.183594 C 49.746094 32.34375 49.261719 32.492188 47.992188 32.949219 C 47.363281 33.179688 46.527344 33.476562 45.519531 33.949219 C 45.027344 34.1875 44.476562 34.472656 43.949219 34.851562 C 43.578125 35.109375 43.199219 35.480469 43.0625 35.816406 C 45.457031 37.054688 47.429688 39.0625 48.816406 42.023438 C 49.761719 41.730469 50.703125 41.523438 51.527344 41.378906 C 52.5 41.207031 53.492188 40.929688 54.5 40.734375 Z M 56.921875 44.039062 C 56.894531 43.601562 56.867188 43.160156 56.746094 42.773438 C 56.644531 42.457031 55.328125 42.785156 54.9375 42.867188 C 53.992188 43.058594 53.046875 43.257812 52.097656 43.445312 C 50.410156 43.765625 46.371094 44.511719 45.59375 46.511719 C 49.339844 45.503906 53.042969 44.28125 56.921875 44.039062 Z M 58.453125 46.804688 C 58.355469 46.570312 58.253906 46.339844 58.152344 46.113281 C 58.117188 46.117188 58.082031 46.125 58.039062 46.125 C 56.007812 46.148438 54.027344 46.496094 52.070312 46.96875 C 52.277344 47.40625 52.578125 47.769531 52.992188 48.136719 C 53.019531 48.164062 53.042969 48.191406 53.070312 48.226562 C 55.074219 47.449219 57.175781 46.957031 58.453125 46.804688 Z M 59.984375 50.285156 C 59.777344 49.800781 59.5625 49.316406 59.355469 48.828125 C 59.253906 48.863281 59.148438 48.894531 59.027344 48.898438 C 57.359375 48.972656 55.574219 49.652344 54.050781 50.28125 C 53.046875 50.695312 52.003906 51.160156 51.117188 51.808594 C 50.8125 52.039062 49.152344 53.460938 50.496094 53.453125 C 53.835938 53.433594 56.867188 51.394531 59.984375 50.285156 Z M 63.53125 53.640625 C 63.144531 53.21875 62.6875 52.890625 62.121094 52.640625 C 62.101562 52.652344 62.085938 52.667969 62.070312 52.683594 C 60.304688 53.898438 58.476562 54.8125 57.410156 56.441406 C 58.417969 55.914062 59.382812 55.304688 60.449219 54.847656 C 61.464844 54.417969 62.535156 54.113281 63.53125 53.640625 Z M 66.539062 55.847656 C 66.160156 55.585938 65.78125 55.328125 65.402344 55.0625 C 64.96875 55.335938 64.515625 55.554688 64.050781 55.75 C 64.402344 55.957031 64.738281 56.183594 65.058594 56.449219 C 65.089844 56.476562 65.109375 56.507812 65.140625 56.535156 C 65.617188 56.277344 66.089844 56.050781 66.539062 55.847656 Z M 69.335938 57.457031 C 67.871094 57.121094 66.46875 58.308594 64.972656 59.003906 C 63.765625 59.566406 62.085938 60.160156 61.285156 61.332031 C 61.40625 61.441406 61.507812 61.578125 61.578125 61.746094 C 61.777344 62.21875 66.570312 59.132812 69.335938 57.457031 Z M 71.996094 59.050781 C 71.78125 58.953125 71.566406 58.859375 71.351562 58.757812 C 71.324219 58.746094 71.292969 58.722656 71.265625 58.710938 C 70.878906 58.910156 70.414062 59.203125 69.902344 59.550781 C 70.394531 59.722656 70.878906 59.925781 71.34375 60.152344 C 71.609375 59.816406 71.832031 59.453125 71.996094 59.050781 Z M 72.988281 62.433594 C 73.875 61.734375 75.398438 61.019531 73.890625 60.058594 C 73.867188 60.054688 73.855469 60.039062 73.832031 60.03125 C 72.84375 62.15625 70.792969 63.25 69.007812 64.707031 C 70.363281 64.84375 72.007812 63.21875 72.988281 62.433594 Z M 79.953125 64.695312 C 80.71875 63.972656 79.480469 63.71875 78.84375 63.613281 C 78.703125 63.585938 78.558594 63.5625 78.414062 63.542969 C 78.378906 63.59375 78.335938 63.640625 78.285156 63.683594 C 77.242188 64.601562 76.070312 65.421875 75.199219 66.507812 C 74.976562 66.789062 74.453125 67.644531 74.917969 67.515625 C 75.535156 67.351562 76.085938 67.046875 76.613281 66.703125 C 77.664062 66.03125 79.050781 65.535156 79.953125 64.695312 Z M 84.726562 67.1875 C 84.75 67.101562 84.765625 67.050781 84.769531 67.011719 C 84.683594 66.945312 84.585938 66.886719 84.492188 66.824219 C 84.464844 66.84375 84.441406 66.875 84.414062 66.894531 C 83.535156 67.511719 82.484375 68.21875 81.910156 69.148438 C 81.160156 70.347656 82.578125 70.140625 83.183594 69.503906 C 83.648438 69.019531 84.0625 68.480469 84.386719 67.890625 C 84.515625 67.660156 84.648438 67.429688 84.726562 67.1875 Z M 86.09375 81.789062 C 86.738281 81.722656 87.382812 81.660156 88.03125 81.585938 C 87.375 77.070312 84.070312 75.746094 79.917969 74.738281 C 77.183594 74.074219 74.519531 73.371094 71.859375 72.445312 C 66.027344 70.398438 60.035156 68.191406 54.90625 64.65625 C 44.8125 57.703125 36.984375 47.820312 31.765625 36.773438 C 31.757812 36.761719 31.757812 36.746094 31.75 36.730469 C 31.515625 36.765625 31.273438 36.804688 31.035156 36.839844 C 32.128906 40.007812 33.746094 42.722656 35.28125 45.148438 C 37.003906 47.8125 38.75 50.113281 40.300781 52.195312 C 43.367188 56.386719 46.164062 59.296875 48.488281 61.304688 C 48.773438 61.554688 49.050781 61.796875 49.324219 62.027344 C 49.601562 62.242188 49.875 62.449219 50.132812 62.640625 C 50.660156 63.027344 51.109375 63.414062 51.570312 63.699219 C 52.027344 63.992188 52.433594 64.265625 52.796875 64.5 C 52.984375 64.621094 53.15625 64.730469 53.320312 64.835938 C 53.484375 64.929688 53.644531 65.023438 53.792969 65.101562 C 54.980469 65.75 55.480469 66.082031 55.453125 66.144531 C 55.421875 66.214844 54.863281 66.015625 53.597656 65.472656 C 53.441406 65.402344 53.269531 65.328125 53.09375 65.25 C 52.921875 65.152344 52.742188 65.050781 52.542969 64.945312 C 52.15625 64.722656 51.726562 64.476562 51.246094 64.207031 C 50.761719 63.933594 50.28125 63.5625 49.730469 63.191406 C 49.460938 63.007812 49.171875 62.804688 48.875 62.597656 C 48.59375 62.371094 48.300781 62.132812 48 61.882812 C 45.570312 59.917969 42.640625 56.984375 39.507812 52.796875 C 37.933594 50.722656 36.160156 48.421875 34.402344 45.71875 C 32.800781 43.230469 31.113281 40.414062 29.964844 37.023438 C 28.210938 37.351562 26.460938 37.761719 24.78125 38.160156 C 21.761719 38.875 14.183594 39.707031 12.648438 42.886719 C 14.855469 41.730469 16.914062 41.042969 18.675781 40.605469 C 20.949219 40.046875 22.742188 39.785156 24.113281 39.621094 C 26.851562 39.296875 27.90625 39.3125 27.925781 39.457031 C 27.949219 39.605469 26.925781 39.855469 24.230469 40.371094 C 22.886719 40.628906 21.125 40.964844 18.929688 41.566406 C 17.007812 42.085938 14.75 42.886719 12.320312 44.289062 C 11.988281 47.035156 12.191406 49.800781 11.960938 52.558594 C 11.773438 54.777344 11.308594 57.015625 10.972656 59.210938 C 10.789062 60.476562 10.582031 61.726562 10.367188 62.96875 C 20.148438 64.792969 26.445312 72.070312 26.488281 81.921875 C 38.050781 82.402344 49.617188 83.28125 61.191406 83.011719 C 69.113281 82.824219 77.105469 82.59375 85.015625 81.886719 C 84.914062 80.800781 84.5625 79.914062 83.96875 79.121094 C 83.261719 78.140625 82.246094 77.597656 81.203125 77.113281 C 79.09375 76.152344 76.941406 75.773438 75.035156 75.351562 C 71.136719 74.542969 68.261719 73.308594 66.148438 72.300781 C 64.039062 71.265625 62.636719 70.449219 61.765625 69.898438 C 60.890625 69.347656 60.542969 69.070312 60.578125 69.003906 C 60.613281 68.941406 61.035156 69.082031 61.964844 69.519531 C 62.894531 69.957031 64.339844 70.65625 66.460938 71.59375 C 68.59375 72.507812 71.421875 73.617188 75.234375 74.351562 C 77.148438 74.753906 79.34375 75.066406 81.648438 76.097656 C 82.785156 76.617188 83.96875 77.304688 84.828125 78.484375 C 85.542969 79.429688 85.964844 80.609375 86.09375 81.789062 Z M 90.296875 70.414062 C 90.589844 70.054688 90.339844 69.898438 89.953125 69.65625 C 89.640625 69.460938 89.324219 69.296875 89.003906 69.160156 C 88.761719 69.90625 88.523438 70.691406 88.480469 71.46875 C 88.480469 71.585938 88.472656 71.699219 88.472656 71.8125 C 88.496094 71.804688 88.519531 71.800781 88.546875 71.777344 C 89.167969 71.421875 89.847656 70.976562 90.296875 70.414062 Z M 93.609375 81.066406 C 93.378906 78.121094 92.054688 75.546875 90.289062 73.230469 C 90.132812 73.328125 89.976562 73.429688 89.824219 73.523438 C 88.632812 74.210938 86.765625 74.386719 86.421875 72.636719 C 86.171875 71.320312 86.507812 69.941406 86.910156 68.667969 C 86.765625 68.660156 86.617188 68.652344 86.464844 68.652344 C 85.835938 70.011719 84.683594 71.335938 83.535156 71.84375 C 81.730469 72.636719 79.210938 71.804688 79.507812 69.476562 C 79.671875 68.253906 80.539062 67.238281 81.53125 66.386719 C 81.496094 66.371094 81.46875 66.359375 81.445312 66.351562 C 81.460938 66.34375 81.476562 66.351562 81.488281 66.359375 C 81.46875 66.351562 81.445312 66.34375 81.433594 66.34375 C 81.410156 66.332031 81.390625 66.332031 81.375 66.324219 C 80.910156 66.695312 80.375 67.003906 79.9375 67.238281 C 79.015625 67.738281 78.152344 68.324219 77.234375 68.832031 C 76.386719 69.3125 75.261719 69.898438 74.253906 69.625 C 73.238281 69.347656 72.566406 68.367188 72.609375 67.300781 C 72.667969 65.964844 73.597656 64.871094 74.65625 63.921875 C 72.367188 65.785156 69.242188 68.527344 66.65625 65.652344 C 66.261719 65.207031 66.21875 64.570312 66.640625 64.136719 C 67.496094 63.242188 68.636719 62.539062 69.671875 61.746094 C 69.164062 61.546875 68.640625 61.375 68.128906 61.191406 C 68.007812 61.148438 67.898438 61.089844 67.804688 61.019531 C 64.78125 63.140625 61.164062 65.394531 59.683594 62.675781 C 59.117188 62.570312 58.648438 62.089844 58.882812 61.390625 C 59.578125 59.386719 61.242188 58.460938 63 57.609375 C 62.742188 57.457031 62.464844 57.328125 62.230469 57.257812 C 61.9375 57.171875 61.699219 56.972656 61.570312 56.714844 C 61.191406 56.871094 60.828125 57.042969 60.46875 57.234375 C 58.960938 58.082031 57.503906 58.945312 55.824219 59.402344 C 54.972656 59.640625 54.386719 58.867188 54.507812 58.085938 C 54.765625 56.421875 55.488281 55.207031 56.453125 54.207031 C 52.898438 55.675781 48.921875 56.800781 47.886719 53.710938 C 47.265625 51.875 48.824219 50.332031 50.988281 49.164062 C 50.554688 48.679688 50.226562 48.121094 49.980469 47.511719 C 48.238281 47.992188 46.492188 48.515625 44.742188 48.949219 C 44.207031 49.078125 43.539062 48.785156 43.425781 48.199219 C 42.898438 45.539062 44.621094 43.851562 46.820312 42.792969 C 44.0625 37.253906 39.230469 36.09375 34.011719 36.480469 C 40.042969 48.90625 49.632812 60.476562 62.335938 66.367188 C 68.921875 69.425781 75.65625 71.046875 82.503906 73.207031 C 86.996094 74.625 89.496094 76.804688 90.15625 81.371094 C 91.292969 81.257812 92.441406 81.15625 93.609375 81.066406 Z M 97.71875 73.988281 C 97.726562 73.988281 97.734375 73.980469 97.738281 73.980469 C 97.71875 73.972656 97.710938 73.964844 97.699219 73.960938 C 97.703125 73.964844 97.710938 73.980469 97.71875 73.988281 Z M 95.730469 80.886719 C 96.539062 80.816406 97.347656 80.742188 98.15625 80.664062 C 97.976562 76.511719 95.089844 74.066406 92.191406 71.390625 C 92.097656 71.542969 92 71.683594 91.890625 71.820312 C 93.953125 74.542969 95.421875 77.441406 95.730469 80.886719 Z M 112.105469 77.789062 C 111.652344 77.742188 111.195312 77.691406 110.722656 77.660156 C 106.785156 77.417969 102.96875 76.640625 99.085938 76.046875 C 99.769531 77.339844 100.214844 78.777344 100.292969 80.449219 C 104.375 79.984375 108.421875 79.257812 112.105469 77.789062 Z M 117.03125 79.269531 C 116.558594 79.007812 116.058594 78.777344 115.535156 78.585938 C 108.269531 82.339844 99.628906 82.402344 91.664062 83.332031 C 82.027344 84.453125 72.273438 84.890625 62.578125 85.117188 C 43.753906 85.5625 24.945312 83.09375 6.148438 83.976562 C 6.082031 85.683594 6.105469 87.394531 6.183594 89.101562 C 6.199219 89.335938 6.378906 94.933594 7.027344 95.085938 C 8.695312 95.484375 10.351562 95.355469 12.046875 95.4375 C 17.308594 95.679688 22.507812 96.050781 27.789062 96.050781 C 39.601562 96.058594 51.410156 96.050781 63.207031 96.480469 C 68.613281 96.671875 74.011719 96.601562 79.410156 96.652344 C 79.480469 96.65625 79.550781 96.65625 79.617188 96.65625 C 80.710938 93.175781 83.097656 88.65625 86.609375 87.144531 C 90.726562 85.375 94.960938 85.890625 99.3125 85.449219 C 102.789062 85.097656 116.320312 83.753906 117.03125 79.269531 Z M 118.710938 91.203125 C 121.578125 90.515625 122.199219 88.464844 121.511719 85.664062 C 120.976562 83.488281 120.082031 81.867188 118.875 80.664062 C 117.128906 84.8125 108.859375 85.992188 105.433594 86.628906 C 101.992188 87.265625 98.675781 87.644531 95.171875 87.757812 C 91.96875 87.863281 88.074219 87.894531 85.714844 90.4375 C 84.027344 92.269531 82.707031 94.355469 81.867188 96.695312 C 86.335938 96.78125 90.839844 96.902344 95.265625 96.335938 C 100.894531 95.628906 106.347656 94.136719 111.839844 92.777344 C 114.121094 92.210938 116.421875 91.753906 118.710938 91.203125 Z M 120.683594 79.207031 C 123.222656 82.082031 126.382812 90.589844 121.253906 92.660156 C 116.929688 94.414062 111.796875 95.027344 107.261719 96.144531 C 102.453125 97.324219 97.582031 98.445312 92.621094 98.71875 C 81.460938 99.339844 70.128906 98.78125 58.960938 98.496094 C 47.171875 98.1875 35.390625 98.289062 23.601562 98.195312 C 18.746094 98.152344 13.855469 97.894531 9.023438 97.53125 C 7.558594 97.414062 4.390625 97.222656 4.523438 95.027344 C 4.675781 92.699219 4.019531 90.289062 4.019531 87.9375 C 4.023438 85.640625 3.925781 83.269531 4.132812 80.988281 C 4.519531 76.746094 6.242188 72.964844 7.113281 68.839844 C 8.300781 63.199219 9.75 57.042969 9.921875 51.273438 C 10.003906 48.585938 9.085938 42.972656 11.066406 40.707031 C 13.269531 38.175781 18.761719 37.425781 21.820312 36.667969 C 25.558594 35.753906 29.363281 34.714844 33.203125 34.328125 C 35.175781 34.128906 37.054688 34.164062 38.816406 34.449219 C 39.886719 31.914062 42.269531 30.992188 44.71875 29.824219 C 46.355469 29.054688 48.644531 27.34375 50.539062 27.988281 C 54.578125 29.367188 55.757812 36.796875 56.660156 40.535156 C 56.824219 40.542969 56.988281 40.542969 57.152344 40.5625 C 58.882812 40.769531 58.839844 42.59375 59.03125 43.96875 C 59.328125 43.988281 59.605469 44.144531 59.777344 44.511719 C 60.675781 46.460938 61.492188 48.449219 62.363281 50.410156 C 62.371094 50.414062 62.371094 50.429688 62.371094 50.4375 C 62.394531 50.445312 62.414062 50.445312 62.4375 50.453125 C 63.832031 50.980469 64.894531 51.738281 65.695312 52.917969 C 65.898438 52.902344 66.097656 52.945312 66.269531 53.0625 C 67.054688 53.589844 67.8125 54.148438 68.59375 54.667969 C 68.804688 54.820312 68.964844 55.019531 69.050781 55.242188 C 70.085938 55.257812 71.109375 55.671875 72.210938 56.714844 C 72.261719 56.765625 72.289062 56.820312 72.332031 56.871094 C 72.367188 56.886719 72.394531 56.894531 72.429688 56.90625 C 74.082031 57.652344 75.847656 58.402344 76.671875 60.125 C 76.8125 60.433594 76.878906 60.71875 76.886719 60.988281 C 76.898438 60.996094 76.90625 60.996094 76.914062 60.996094 C 78.578125 61.65625 81.859375 61.648438 82.363281 63.664062 C 82.390625 63.671875 82.425781 63.671875 82.453125 63.675781 C 83.820312 64.097656 86.535156 64.835938 86.902344 66.503906 C 88.816406 66.582031 91.132812 67.265625 92.191406 68.875 C 92.199219 68.882812 92.199219 68.890625 92.207031 68.90625 C 92.441406 68.960938 92.664062 69.03125 92.898438 69.148438 C 93.042969 69.21875 93.15625 69.328125 93.242188 69.453125 C 93.257812 69.46875 93.277344 69.484375 93.300781 69.496094 C 93.964844 70.128906 94.628906 70.742188 95.273438 71.355469 C 95.902344 71.785156 96.488281 72.179688 97.039062 72.5 C 98.289062 73.265625 99.34375 73.738281 100.207031 74.042969 C 104.355469 74.617188 108.472656 75.175781 112.625 75.667969 C 115.765625 76.046875 118.53125 76.777344 120.683594 79.207031"></path><path fill="inherit" d="M 40.4375 38.53125 C 42.046875 38.453125 43.746094 39.519531 43.617188 41.300781 C 43.488281 42.996094 41.722656 44.082031 40.117188 43.945312 C 38.679688 43.824219 37.5 42.523438 37.628906 41.042969 C 37.757812 39.570312 38.816406 38.460938 40.351562 38.53125 C 40.367188 38.53125 40.378906 38.53125 40.394531 38.53125 C 40.410156 38.53125 40.421875 38.53125 40.4375 38.53125 Z M 39.9375 41.664062 C 39.957031 41.671875 40.042969 41.742188 40.058594 41.75 C 40.082031 41.765625 40.074219 41.765625 40.085938 41.773438 C 40.152344 41.792969 40.207031 41.808594 40.273438 41.816406 C 40.273438 41.808594 40.542969 41.800781 40.601562 41.785156 C 40.808594 41.734375 41.003906 41.6875 41.1875 41.566406 C 41.324219 41.480469 41.34375 41.472656 41.410156 41.363281 C 41.421875 41.328125 41.46875 41.171875 41.472656 41.171875 C 41.46875 41.058594 41.402344 40.898438 41.351562 40.863281 C 41.074219 40.683594 40.824219 40.65625 40.4375 40.679688 C 40.421875 40.679688 40.410156 40.671875 40.394531 40.671875 C 40.378906 40.671875 40.367188 40.679688 40.351562 40.679688 C 40.117188 40.664062 40.164062 40.636719 40.03125 40.683594 C 40.03125 40.683594 40.023438 40.691406 40.007812 40.691406 C 39.988281 40.714844 39.953125 40.726562 39.921875 40.75 C 39.921875 40.785156 39.808594 40.984375 39.808594 40.929688 C 39.792969 40.972656 39.78125 41.023438 39.773438 41.070312 C 39.773438 41.085938 39.765625 41.105469 39.765625 41.144531 C 39.773438 41.429688 39.714844 41.144531 39.808594 41.421875 C 39.816406 41.457031 39.824219 41.480469 39.824219 41.492188 C 39.828125 41.5 39.835938 41.507812 39.84375 41.523438 C 39.863281 41.570312 39.902344 41.613281 39.929688 41.65625 C 39.929688 41.65625 39.929688 41.65625 39.9375 41.664062"></path></g></svg>
```

## assets/illustrations/phone-green.svg

```svg
<?xml version="1.0"?><svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" contentScriptType="text/ecmascript" fill="#62cc74" width="47.3" zoomAndPan="magnify" contentStyleType="text/css" viewBox="26.3 1.7 47.3 96.7" height="96.7" preserveAspectRatio="xMidYMid meet" version="1"><g id="change1_1"><path d="M67.485,98.344H32.514c-3.408,0-6.171-2.764-6.171-6.172V7.828 c0-3.408,2.763-6.171,6.171-6.171h34.972c3.408,0,6.172,2.763,6.172,6.171v84.344C73.657,95.58,70.894,98.344,67.485,98.344z M50,96.285c2.272,0,4.114-1.842,4.114-4.113c0-2.273-1.842-4.115-4.114-4.115s-4.114,1.842-4.114,4.115 C45.886,94.443,47.728,96.285,50,96.285z M41.771,6.8c-0.568,0-1.028,0.46-1.028,1.028c0,0.568,0.46,1.029,1.028,1.029 c0.567,0,1.028-0.46,1.028-1.029C42.8,7.26,42.339,6.8,41.771,6.8z M50,2.686c-0.568,0-1.028,0.46-1.028,1.028 c0,0.568,0.46,1.029,1.028,1.029c0.567,0,1.028-0.46,1.028-1.029C51.028,3.146,50.567,2.686,50,2.686z M54.114,6.8h-8.229 c-0.568,0-1.028,0.46-1.028,1.028c0,0.568,0.46,1.029,1.028,1.029h8.229c0.568,0,1.028-0.46,1.028-1.029 C55.143,7.26,54.683,6.8,54.114,6.8z M70.571,11.943H29.429V86h41.143V11.943z M50,89.086c1.704,0,3.086,1.381,3.086,3.086 c0,1.703-1.382,3.086-3.086,3.086s-3.086-1.383-3.086-3.086C46.914,90.467,48.296,89.086,50,89.086z" clip-rule="evenodd" fill-rule="evenodd"></path></g></svg>
```

## assets/illustrations/meal-pink.svg

```svg
<?xml version="1.0"?><svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" contentScriptType="text/ecmascript" fill="#ffa6d0" width="298.7" zoomAndPan="magnify" contentStyleType="text/css" viewBox="100.6 100.7 298.7 298.7" height="298.7" preserveAspectRatio="xMidYMid meet" version="1"><g id="change1_1"><path d="M250,100.65c82.49,0,149.35,66.87,149.35,149.35c0,62.95-38.95,116.8-94.07,138.78l-2.18-47.06l0-0.09 c0.12-9.31,4.05-16.64,12.77-20.33l1.12-0.45l0.06-0.02l0.07-0.03l0.11-0.04c6.42-2.6,11.65-6.1,15.21-12.16 c4.45-7.55,5.31-17.61,5.31-26.17c0-16.46-4.85-35.89-13.21-50.12c-5.94-10.11-15.31-20.34-27.96-20.34 c-12.65,0-22.02,10.23-27.96,20.34c-8.36,14.23-13.21,33.66-13.21,50.12c0,8.57,0.86,18.63,5.31,26.17 c3.6,6.1,8.89,9.61,15.34,12.21c0.18,0.07,0.36,0.15,0.54,0.22h0.05l0.56,0.24c8.75,3.68,12.73,10.93,12.85,20.36l0,0.09 l-2.45,52.86c-12.02,3.12-24.62,4.78-37.61,4.78c-13.45,0-26.48-1.79-38.88-5.12l-2.29-49.49l0-0.11 c0.12-9.54,4.19-17.06,13.12-20.84l1.14-0.45l0.04-0.01l0.04-0.02l0.13-0.05c6.3-2.55,11.44-5.98,14.94-11.93 c4.39-7.45,5.23-17.44,5.23-25.89c0-0.82-0.03-1.64-0.08-2.46c-0.03-0.47-0.07-0.94-0.13-1.4l-0.08-0.69l0.13-0.47l-5.43-63.17 l-5.68,0.01l-0.49,66.76l-9.46,0.94l-5.62-75.46l-6.16,0.37l-1.22,76.02l-3.35,0.14c-0.7,0.03-1.4,0.04-2.09,0.04 c-0.7,0-1.41-0.01-2.11-0.04l-3.33-0.14l-1.71-76.02l-6.16-0.36l-5.13,75.46l-9.47-0.94l-0.48-66.77l-5.71,0l-7.34,63.19l0.12,0.45 l-0.08,0.67c-0.05,0.47-0.09,0.94-0.12,1.41c-0.05,0.82-0.08,1.64-0.08,2.46c0,8.45,0.84,18.44,5.23,25.89 c3.53,6,8.73,9.43,15.07,11.98c0.15,0.06,0.3,0.12,0.44,0.18h0.05l0.66,0.28c8.95,3.77,13.06,11.21,13.19,20.86l0,0.11l-2.04,44.1 c-55.19-21.94-94.2-75.83-94.2-138.84C100.65,167.51,167.51,100.65,250,100.65" clip-rule="evenodd" fill-rule="evenodd"></path></g></svg>
```

## assets/illustrations/laptop-purple.svg

```svg
<?xml version="1.0"?><svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" contentScriptType="text/ecmascript" fill="#8428fa" width="900" zoomAndPan="magnify" contentStyleType="text/css" viewBox="50.0 223.5 900.0 553.0" height="553" preserveAspectRatio="xMidYMid meet" version="1"><g id="change1_1"><path fill="inherit" d="M 938.472656 766.621094 L 61.542969 766.621094 L 61.542969 750.539062 L 938.472656 750.539062 Z M 938.8125 740.6875 L 61.199219 740.6875 C 55.867188 740.6875 51.691406 744.113281 51.691406 748.488281 L 51.691406 768.671875 C 51.691406 773.046875 55.867188 776.476562 61.199219 776.476562 L 938.8125 776.476562 C 944.148438 776.476562 948.324219 773.046875 948.324219 768.671875 L 948.324219 748.488281 C 948.324219 744.113281 944.148438 740.6875 938.8125 740.6875"></path><path fill="inherit" d="M 600.238281 729.1875 C 601.875 728.75 603.246094 727.996094 604.230469 726.953125 C 606.449219 724.65625 606.441406 721.472656 604.226562 718.847656 L 586.75 697.925781 C 584.660156 695.460938 580.347656 693.808594 576.019531 693.808594 L 423.996094 693.808594 C 419.707031 693.808594 415.285156 695.507812 413.25 697.941406 L 395.796875 718.835938 C 393.566406 721.480469 393.566406 724.675781 395.765625 726.9375 C 396.753906 727.988281 398.128906 728.746094 399.777344 729.1875 L 66.714844 729.1875 L 141.484375 639.753906 C 142.515625 638.835938 147.613281 636.734375 152.082031 636.734375 L 847.933594 636.734375 C 852.574219 636.734375 857.609375 638.855469 858.648438 639.8125 L 933.300781 729.1875 Z M 596.734375 723.710938 L 403.28125 723.710938 C 401.445312 723.710938 400.4375 723.21875 400.113281 722.925781 C 400.15625 722.855469 400.222656 722.757812 400.324219 722.636719 L 417.785156 701.734375 C 418.476562 700.910156 421.082031 699.71875 423.996094 699.71875 L 576.019531 699.71875 C 578.796875 699.71875 581.414062 700.773438 582.230469 701.734375 L 599.699219 722.648438 C 599.796875 722.765625 599.859375 722.855469 599.898438 722.925781 C 599.578125 723.21875 598.570312 723.710938 596.734375 723.710938 Z M 950 739.039062 L 948.121094 732.710938 C 947.785156 731.582031 947.144531 730.445312 946.101562 729.144531 L 866.121094 633.390625 C 863.125 629.863281 854.792969 626.882812 847.933594 626.882812 L 152.082031 626.882812 C 146.03125 626.882812 137.085938 629.570312 133.957031 633.394531 L 53.960938 729.078125 C 52.925781 730.339844 52.25 731.519531 51.898438 732.699219 L 50 739.039062 L 950 739.039062"></path><path fill="inherit" d="M 418.386719 716.519531 L 426.390625 706.90625 L 573.628906 706.90625 L 581.660156 716.519531 Z M 423.621094 700.992188 L 405.773438 722.433594 L 594.300781 722.433594 L 576.390625 700.992188 L 423.621094 700.992188"></path><path fill="inherit" d="M 152.070312 242.199219 C 152.070312 237.335938 156.027344 233.378906 160.890625 233.378906 L 839.1875 233.378906 C 844.054688 233.378906 848.011719 237.335938 848.011719 242.199219 L 848.011719 599.683594 C 848.011719 604.546875 844.054688 608.503906 839.1875 608.503906 L 160.890625 608.503906 C 156.027344 608.503906 152.070312 604.546875 152.070312 599.683594 Z M 160.890625 618.355469 L 839.1875 618.355469 C 849.484375 618.355469 857.863281 609.980469 857.863281 599.683594 L 857.863281 242.199219 C 857.863281 231.902344 849.484375 223.523438 839.1875 223.523438 L 160.890625 223.523438 C 150.59375 223.523438 142.214844 231.902344 142.214844 242.199219 L 142.214844 599.683594 C 142.214844 609.980469 150.59375 618.355469 160.890625 618.355469"></path></g></svg>
```

## assets/illustrations/path-dashed-1.svg

```svg
<?xml version="1.0"?><svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" contentScriptType="text/ecmascript" fill="#8428fa" width="790.2" zoomAndPan="magnify" contentStyleType="text/css" viewBox="-0.5 -0.0 790.2 532.3" height="532.3" preserveAspectRatio="xMidYMid meet" version="1"><g data-name="Layer 2"><g id="change1_1" data-name="Layer 1"><path d="M781.48,29l-.55,0a7.5,7.5,0,0,1-6.94-8c.61-8.36.68-13.47.68-13.52A7.5,7.5,0,0,1,782.17,0h.09a7.5,7.5,0,0,1,7.41,7.59c0,.22-.07,5.57-.72,14.43A7.5,7.5,0,0,1,781.48,29Z"></path><path d="M15.73,491.4a7.33,7.33,0,0,1-1.9-.24A7.5,7.5,0,0,1,8.46,482c2.42-9.3,5.19-18.32,8.24-26.81a7.5,7.5,0,1,1,14.12,5.06c-2.89,8.07-5.53,16.66-7.84,25.53A7.5,7.5,0,0,1,15.73,491.4ZM34.34,440a7.42,7.42,0,0,1-3.28-.76,7.5,7.5,0,0,1-3.45-10,213.15,213.15,0,0,1,14-24.63,7.5,7.5,0,0,1,12.49,8.3,199.3,199.3,0,0,0-13.06,22.91A7.51,7.51,0,0,1,34.34,440Zm30.42-45.31a7.51,7.51,0,0,1-5.51-12.59,161.14,161.14,0,0,1,21.24-19.28,7.5,7.5,0,0,1,9,12,145.68,145.68,0,0,0-19.25,17.48A7.46,7.46,0,0,1,64.76,394.68Zm314.63-1.38c-2.3,0-4.63,0-6.94-.13a7.5,7.5,0,1,1,.58-15,158.42,158.42,0,0,0,26.09-1.12A7.5,7.5,0,0,1,401,391.94,171.21,171.21,0,0,1,379.39,393.3Zm-33.85-3.19a8,8,0,0,1-1.37-.12,227.06,227.06,0,0,1-27.46-6.91,7.5,7.5,0,1,1,4.54-14.29,214.26,214.26,0,0,0,25.64,6.45,7.5,7.5,0,0,1-1.35,14.87ZM426.77,386a7.5,7.5,0,0,1-2.35-14.62,118.49,118.49,0,0,0,23.41-10.62,7.5,7.5,0,0,1,7.68,12.89,133.55,133.55,0,0,1-26.39,12A7.41,7.41,0,0,1,426.77,386Zm-133.4-12.28a7.6,7.6,0,0,1-3-.64c-1.55-.68-3.1-1.39-4.66-2.11-6.65-3.08-13.43-5.93-20.16-8.47a7.5,7.5,0,1,1,5.29-14c7.07,2.67,14.19,5.66,21.17,8.89,1.48.68,2.95,1.35,4.42,2a7.51,7.51,0,0,1-3,14.37ZM108.3,362A7.5,7.5,0,0,1,105,347.74a156.82,156.82,0,0,1,26.83-10.25,7.5,7.5,0,1,1,4.06,14.44,142.42,142.42,0,0,0-24.27,9.26A7.37,7.37,0,0,1,108.3,362Zm365-4a7.5,7.5,0,0,1-5.31-12.8,89.38,89.38,0,0,0,15.15-20.12,7.5,7.5,0,0,1,13.16,7.21,104.65,104.65,0,0,1-17.69,23.5A7.49,7.49,0,0,1,473.27,358Zm-231.16-3.44a7.46,7.46,0,0,1-2-.26,253.11,253.11,0,0,0-26-5.62,7.5,7.5,0,0,1,2.37-14.81,267,267,0,0,1,27.55,6,7.5,7.5,0,0,1-2,14.74ZM160.7,347a7.5,7.5,0,0,1-.8-15A193.49,193.49,0,0,1,181.08,331c2.34,0,4.83,0,7.26.13a7.5,7.5,0,1,1-.52,15c-2.23-.08-4.48-.12-6.67-.12h-.07A178.66,178.66,0,0,0,161.53,347,7.69,7.69,0,0,1,160.7,347Zm338.46-36.49a7.6,7.6,0,0,1-2-.28,7.5,7.5,0,0,1-5.18-9.25,105.9,105.9,0,0,1,11.76-26.9A7.5,7.5,0,1,1,516.47,282a90.68,90.68,0,0,0-10.09,23.09A7.51,7.51,0,0,1,499.16,310.55Zm28.23-46.1a7.5,7.5,0,0,1-5.16-12.94A147,147,0,0,1,545.1,234a7.5,7.5,0,0,1,8,12.7,132.47,132.47,0,0,0-20.54,15.73A7.47,7.47,0,0,1,527.39,264.45ZM573.27,235a7.5,7.5,0,0,1-3.1-14.34c8-3.61,16.77-7.07,26.13-10.29a7.5,7.5,0,1,1,4.89,14.18c-8.93,3.07-17.28,6.36-24.84,9.78A7.51,7.51,0,0,1,573.27,235Zm51.66-18.06a7.5,7.5,0,0,1-2-14.73c8.4-2.3,17.46-4.54,26.94-6.67a7.5,7.5,0,0,1,3.28,14.64c-9.25,2.08-18.09,4.26-26.26,6.5A7.61,7.61,0,0,1,624.93,216.92Zm53.44-12.12A7.5,7.5,0,0,1,677,189.93l2.47-.47a79.89,79.89,0,0,0,21.45-7.27,7.5,7.5,0,0,1,6.8,13.38,94.86,94.86,0,0,1-25.48,8.63l-2.44.47A8.6,8.6,0,0,1,678.37,204.8Zm48.11-24.3a7.5,7.5,0,0,1-5.19-12.92,114.44,114.44,0,0,0,16.31-19.81A7.5,7.5,0,0,1,750.13,156a129.79,129.79,0,0,1-18.47,22.4A7.47,7.47,0,0,1,726.48,180.5Zm30.46-45.16a7.5,7.5,0,0,1-6.83-10.57A229.47,229.47,0,0,0,759.48,100a7.5,7.5,0,1,1,14.3,4.51,243.55,243.55,0,0,1-10,26.46A7.5,7.5,0,0,1,756.94,135.34Zm16.72-52.13a7.53,7.53,0,0,1-7.33-9.11c1.87-8.5,3.47-17.39,4.77-26.45A7.5,7.5,0,0,1,786,49.78c-1.35,9.42-3,18.68-5,27.53A7.5,7.5,0,0,1,773.66,83.21Z"></path><path d="M7.51,532.33a7,7,0,0,1-1.11-.08,7.51,7.51,0,0,1-6.32-8.52c.7-4.73,1.48-9.46,2.32-14.06a7.5,7.5,0,0,1,14.75,2.68c-.8,4.44-1.55,9-2.23,13.58A7.49,7.49,0,0,1,7.51,532.33Z"></path></g></g></svg>
```

## assets/illustrations/path-dashed-2.svg

```svg
<?xml version="1.0"?><svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" contentScriptType="text/ecmascript" fill="#000000" width="500.1" zoomAndPan="magnify" contentStyleType="text/css" viewBox="0.0 0.0 500.1 267.4" height="267.4" preserveAspectRatio="xMidYMid meet" version="1"><g id="change1_1"><path fill="#8428fa" d="M217.5,217.3l0.8,4.6c-3.1,0.5-6.2,0.8-9.4,0.7c-3.1-0.1-6.3-0.6-9.3-1.4l1.2-4.5c2.7,0.7,5.5,1.2,8.3,1.3 C212,218,214.8,217.8,217.5,217.3z M234.3,210.6c-2.4,1.5-4.9,2.9-7.5,4l1.8,4.3c2.9-1.2,5.6-2.7,8.2-4.3c2.6-1.7,5-3.6,7.4-5.6 l-3.1-3.4C238.9,207.3,236.7,209,234.3,210.6z M247.7,198.3l3.6,2.9c1.9-2.4,3.6-5,5.1-7.7c1.5-2.7,2.9-5.5,3.9-8.4l-4.3-1.6 C254.1,188.8,251.2,193.8,247.7,198.3z M263.3,160.8c-0.2-1.5-0.5-3-0.7-4.6l-4.5,0.9c0.2,1.4,0.5,2.8,0.7,4.2l0.3,4.3 c0.1,2.8,0,5.6-0.5,8.4l4.6,0.7c0.5-3.1,0.7-6.2,0.5-9.3L263.3,160.8z M251.8,139.9c0.7,1.2,1.3,2.6,1.9,3.9 c0.3,0.7,0.7,1.3,0.9,1.9l0.7,2l4.3-1.6l-0.8-2.2c-0.3-0.7-0.6-1.4-1-2.1c-0.7-1.4-1.3-2.8-2-4.1l-2.3-4c-0.8-1.3-1.7-2.5-2.6-3.8 l-3.7,2.7c0.8,1.2,1.7,2.3,2.4,3.5L251.8,139.9z M241.8,119.5l-0.9-0.8l-3.4-3c-2.4-1.9-4.8-3.8-7.4-5.4l-2.5,3.9 c2.5,1.5,4.7,3.4,7,5.1l3.2,2.9l0.8,0.7l0.8,0.8l1.5,1.6l3.3-3.2l-1.6-1.6L241.8,119.5z M193,101.8l0.5-4.6 c-6.1-0.7-12.1-0.7-18.2-0.3l0.3,4.6C181.5,101.1,187.3,101.1,193,101.8z M165,98c-6,1-11.9,2.5-17.6,4.3l1.4,4.4 c5.6-1.7,11.2-3.1,17-4.1L165,98z M121.4,113.6l2.2,4.1c5.1-2.8,10.4-5.3,15.8-7.5l-1.7-4.3C132.1,108.1,126.6,110.6,121.4,113.6z M105,123.8l-7.2,5.4l2.8,3.6l7-5.3c2.4-1.7,4.9-3.2,7.3-4.8l-2.5-3.9C110,120.5,107.5,122.1,105,123.8z M86.5,138.7l-3.3,3.1 l-3.3,3.1c-0.5,0.5-1.1,1-1.6,1.6l-1.6,1.6l3.3,3.2l1.5-1.6c0.5-0.5,1.1-1,1.6-1.5l3.2-3l3.2-3c1.1-1,2.2-1.9,3.3-2.9l-3-3.5 C88.7,136.8,87.5,137.7,86.5,138.7z M63.8,162.4c-1,1.1-1.9,2.3-2.9,3.5l-2.8,3.5l3.6,2.9l2.8-3.5c0.9-1.2,1.8-2.3,2.8-3.4l5.8-6.7 l-3.4-3.1L63.8,162.4z M41.6,192.1l3.9,2.6c3.3-4.9,6.6-9.8,10.2-14.5l-3.7-2.7C48.3,182.3,45,187.2,41.6,192.1z M31.4,208.3 c-1.6,2.5-3.1,5.1-4.6,7.7l4,2.3c1.5-2.6,3-5.1,4.5-7.6c1.6-2.5,3-5.1,4.7-7.5l-3.9-2.5C34.5,203.2,33,205.8,31.4,208.3z M17.4,232.7l-4.3,7.8l4.1,2.2l4.2-7.8l4.3-7.7l-4-2.3L17.4,232.7z M0,265.3l4.1,2.1l8.3-15.8l-4.1-2.2L0,265.3z M495.6,0l-3,8.2 c-1.1,2.7-2.4,5.3-3.6,8l4.2,2c1.2-2.8,2.5-5.5,3.7-8.3l3.2-8.5L495.6,0z M479.6,32.5c-1.6,2.4-3.4,4.7-5.1,7.1l3.7,2.8 c1.7-2.5,3.6-4.9,5.3-7.4c1.6-2.6,3.2-5.1,4.8-7.7l-4-2.3C482.8,27.5,481.2,30,479.6,32.5z M462.2,53.8c-1,1.1-2.1,2-3.2,3l-3.2,3 l3.1,3.4l3.3-3.1c1.1-1,2.2-2,3.2-3.1c2.1-2.2,4.2-4.4,6.2-6.6l-3.5-3C466.3,49.5,464.2,51.6,462.2,53.8z M441.2,71.4 c-1.2,0.9-2.4,1.6-3.7,2.4l-3.7,2.3l2.4,4l3.8-2.4c1.3-0.8,2.6-1.6,3.8-2.5c2.4-1.8,4.9-3.5,7.3-5.3l-2.8-3.6 C445.9,68,443.5,69.7,441.2,71.4z M421.1,82.9l-4,1.8c-1.3,0.6-2.7,1.2-4,1.7L409,88l1.6,4.4l4.2-1.6c1.4-0.5,2.8-1.1,4.2-1.7 l4.1-1.9c1.4-0.6,2.8-1.2,4.1-2l-2.1-4.1C423.8,81.8,422.4,82.3,421.1,82.9z M382.4,94.7l0.7,4.6c6-0.9,11.9-2.2,17.7-3.7l-1.2-4.5 C393.8,92.6,388.1,93.8,382.4,94.7z M363.6,96.3c-2.9,0.1-5.9,0.2-8.8,0.2l0,4.6c3,0,6-0.1,9-0.2c3-0.2,6-0.3,9-0.6l-0.4-4.6 C369.5,96.1,366.5,96.2,363.6,96.3z M326.7,100c5.9,0.4,11.9,0.7,17.9,0.9l0.1-4.6c-5.9-0.2-11.8-0.5-17.7-0.9L326.7,100z M298.8,98 c5.9,0.4,11.8,0.8,17.7,1.3l0.3-4.6c-5.9-0.4-11.8-0.9-17.8-1.3L298.8,98z M270.9,92.6l0.1,4.6c5.9-0.1,11.8,0,17.7,0.3l0.2-4.6 C282.9,92.6,276.9,92.5,270.9,92.6z M261,97.7l-0.3-4.6c-6,0.4-12,1.1-17.9,2.1l0.8,4.6C249.3,98.8,255.1,98.1,261,97.7z M231.6,102.2l2.1-0.5l-1.1-4.5l-2.2,0.5l-2.2,0.6l-4.4,1.2l-4.3,1.5c-0.7,0.3-1.4,0.5-2.1,0.7l-1.9,0.8l-2.9-1.1 c-1.4-0.6-2.9-0.9-4.4-1.4c-1.5-0.4-2.9-0.9-4.4-1.2l-1,4.5c1.4,0.3,2.8,0.7,4.2,1.1c1.4,0.4,2.8,0.7,4.1,1.3l4,1.5l3.9,1.8l1.8-3.7 c0.1,0,0.2-0.1,0.3-0.1l4.1-1.4l4.2-1.2L231.6,102.2z M202.4,114.3l1.9-1.1c1.3-0.7,2.5-1.5,3.8-2.1l-2.1-4.1 c-1.3,0.7-2.6,1.5-4,2.2l-2,1.1c-0.6,0.4-1.3,0.8-1.9,1.3l-3.8,2.6l-3.6,2.8l2.9,3.6l3.4-2.7l3.6-2.4 C201.2,115.1,201.7,114.7,202.4,114.3z M186.3,127.3l-3.4-3.2c-4.2,4.5-7.7,9.7-10.4,15.2l4.1,2 C179.3,136.3,182.4,131.5,186.3,127.3z M173,150.5l-4.4-1.4c-1.8,5.8-3,11.9-3.3,18l4.6,0.3C170.2,161.7,171.3,156,173,150.5z M170.1,177.2l-4.6,0.5c0.3,3.1,0.9,6.1,1.6,9.1c0.8,3,1.8,5.9,3,8.8l4.2-1.9c-1.1-2.6-2-5.3-2.8-8 C171,182.9,170.4,180.1,170.1,177.2z M179.2,202l-3.7,2.8c1.9,2.5,4,4.8,6.4,6.9c2.4,2,4.9,3.9,7.7,5.4l2.2-4.1 c-2.5-1.3-4.7-3-6.9-4.8C182.8,206.3,180.9,204.3,179.2,202z"></path></g></svg>
```

## assets/illustrations/path-dashed-3.svg

```svg
<?xml version="1.0"?><svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" contentScriptType="text/ecmascript" fill="#000000" width="500" zoomAndPan="magnify" contentStyleType="text/css" viewBox="0.0 0.1 500.0 191.8" height="191.8" preserveAspectRatio="xMidYMid meet" version="1"><g id="change1_1"><path fill="#8428fa" d="M500,1.6c-2.5,6.9-5.7,13.5-9.4,19.9l-3.9-2.3c3.6-6.1,6.6-12.5,9-19.1L500,1.6z M466.3,45.3l3.2,3.2 c5.2-5.1,10-10.7,14.3-16.6l-3.7-2.7C475.9,35,471.3,40.3,466.3,45.3z M440.1,66.1l2.5,3.8c6.1-3.9,12-8.2,17.6-12.9l-2.9-3.5 C451.9,58.1,446.1,62.2,440.1,66.1z M410.5,81.6l1.8,4.2c6.7-2.8,13.3-6,19.6-9.5l-2.2-4C423.4,75.7,417,78.8,410.5,81.6z M378.7,92.4l1.2,4.4c7-1.8,14-4,20.8-6.5l-1.5-4.3C392.4,88.5,385.6,90.6,378.7,92.4z M345.7,98.7l0.6,4.5 c7.2-0.9,14.4-2.1,21.5-3.6l-0.9-4.5C359.8,96.7,352.8,97.9,345.7,98.7z M312.1,101.5l0.2,4.5c7.2-0.3,14.4-0.8,21.6-1.5l-0.4-4.5 C326.4,100.7,319.2,101.2,312.1,101.5z M289,102.1l-10.8,0l0,4.5l10.8,0c3.6,0,7.2-0.1,10.8-0.2l-0.1-4.5 C296.2,102,292.6,102.1,289,102.1z M244.3,106.1l21.6,0.4l0.1-4.5l-21.6-0.4L244.3,106.1z M210.4,105.7c7.2,0,14.4,0.1,21.5,0.2 l0.1-4.5c-7.2-0.1-14.4-0.2-21.6-0.2L210.4,105.7z M176.4,102l0.2,4.5c7.2-0.4,14.3-0.6,21.5-0.7l-0.1-4.5 C190.8,101.4,183.6,101.6,176.4,102z M142.4,105.2l0.7,4.5c7.1-1,14.2-1.8,21.3-2.4l-0.4-4.5C156.8,103.3,149.6,104.1,142.4,105.2z M109,112.1l1.2,4.4c6.9-1.9,13.8-3.5,20.8-4.8l-0.9-4.5C123.1,108.6,116,110.2,109,112.1z M76.7,123.4l1.8,4.2 c6.5-2.8,13.2-5.4,20-7.6l-1.4-4.3C90.2,118,83.4,120.5,76.7,123.4z M46.5,139.8l2.5,3.8c5.9-3.9,12.1-7.5,18.4-10.7l-2.1-4.1 C58.9,132.1,52.6,135.7,46.5,139.8z M20.2,161.8l3.3,3.1c4.9-5.1,10.1-9.9,15.7-14.3l-2.8-3.6C30.7,151.6,25.3,156.5,20.2,161.8z M0,189.7l4,2.2c3.4-6.2,7.3-12.1,11.6-17.7l-3.6-2.8C7.5,177.1,3.5,183.3,0,189.7z"></path></g></svg>
```

## assets/illustrations/path-dashed-4.svg

```svg
<?xml version="1.0"?><svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" contentScriptType="text/ecmascript" fill="#000000" width="76.6" zoomAndPan="magnify" contentStyleType="text/css" viewBox="10.5 23.3 76.6 53.2" height="53.2" preserveAspectRatio="xMidYMid meet" version="1"><g><g id="change1_3"><path fill="#8428fa" d="M11.6 76.5L10.5 76.4 10.6 75.3 11.7 75.4z"></path></g><g id="change1_2"><path fill="#8428fa" d="M11.8,73.2l-1.1-0.1c0-0.7,0.1-1.5,0.2-2.2L12,71C11.9,71.7,11.8,72.4,11.8,73.2z M12.2,68.8l-1.1-0.1 c0.1-0.7,0.2-1.5,0.3-2.2l1.1,0.2C12.3,67.3,12.2,68.1,12.2,68.8z M39.6,65.8c-0.3,0-0.6,0-0.9-0.1c-0.2-0.1-0.5-0.1-0.7-0.3 l0.5-1c0.2,0.1,0.3,0.1,0.5,0.2c0.4,0.1,0.8,0.1,1.3,0l0.3,1.1C40.2,65.8,39.9,65.8,39.6,65.8z M42.7,64.5l-0.8-0.8 c0.2-0.2,0.4-0.4,0.5-0.6c0.2-0.3,0.4-0.7,0.6-1.1l1,0.4c-0.2,0.5-0.4,0.9-0.7,1.3C43.1,64,42.9,64.3,42.7,64.5z M12.8,64.5 l-1.1-0.2c0.1-0.7,0.3-1.5,0.5-2.2l1.1,0.3C13.1,63.1,12.9,63.8,12.8,64.5z M36.2,63.8c-0.4-0.6-0.7-1.4-0.9-2.2l0-0.1h0.5 l0.5-0.3l0.1,0.2l0,0c0.2,0.7,0.4,1.3,0.8,1.8L36.2,63.8z M13.9,60.3l-1.1-0.3c0.2-0.5,0.3-1,0.5-1.5c0.1-0.2,0.1-0.4,0.2-0.6 l1,0.4c-0.1,0.2-0.1,0.4-0.2,0.6C14.2,59.3,14,59.8,13.9,60.3z M44.5,60.2l-1.1-0.1c0-0.3,0-0.6,0-0.8l0-0.2c0-0.3,0-0.7-0.1-1 l1.1-0.1c0,0.4,0.1,0.8,0.1,1.1l0,0.2C44.6,59.6,44.6,59.9,44.5,60.2z M36.2,59.3l-1.1-0.1c0.1-0.8,0.2-1.5,0.5-2.3l1.1,0.4 C36.4,58,36.3,58.7,36.2,59.3z M15.5,56.3l-1-0.5c0.3-0.7,0.7-1.3,1.1-2l0.9,0.6C16.2,55,15.8,55.6,15.5,56.3z M43,55.9 c-0.2-0.7-0.4-1.3-0.7-2l1-0.5c0.3,0.7,0.6,1.4,0.8,2.2L43,55.9z M37.6,55.5l-0.9-0.6c0.4-0.6,0.9-1.2,1.5-1.8l0.8,0.8 C38.4,54.4,38,54.9,37.6,55.5z M40.6,52.7l-0.5-1c0.2-0.1,0.5-0.2,0.7-0.3c-0.3-0.3-0.5-0.7-0.8-1l0.8-0.8 c0.4,0.4,0.8,0.9,1.1,1.3c0.1,0,0.3-0.1,0.4-0.1l0.2,1.1C41.9,52.2,41.2,52.4,40.6,52.7z M17.8,52.7L16.9,52 c0.5-0.6,1-1.2,1.5-1.7l0.8,0.8C18.7,51.5,18.2,52.1,17.8,52.7z M50.1,52.5c-0.4,0-0.8,0-1.2-0.1l0.1-1.1c0.7,0.1,1.5,0.1,2.1,0 l0.2,1.1C50.9,52.5,50.5,52.5,50.1,52.5z M46.7,52.1c-0.7-0.1-1.4-0.2-2.1-0.2l0.1-1.1c0.8,0,1.5,0.2,2.2,0.3L46.7,52.1z M53.5,51.6l-0.6-1c0.6-0.3,1.1-0.8,1.5-1.3l0.9,0.7C54.8,50.7,54.2,51.2,53.5,51.6z M20.8,49.6l-0.7-0.9c0.6-0.5,1.2-0.9,1.8-1.3 l0.6,0.9C21.9,48.7,21.3,49.1,20.8,49.6z M38.4,49c-0.2-0.1-0.3-0.2-0.5-0.4c-0.4-0.3-0.8-0.6-1.3-0.8l0.5-1 c0.5,0.3,1,0.6,1.4,0.9c0.2,0.1,0.3,0.3,0.5,0.4L38.4,49z M56.4,48l-1-0.4c0.2-0.6,0.4-1.3,0.6-2l1.1,0.2 C56.9,46.6,56.7,47.3,56.4,48z M24.4,47.3l-0.5-1c0.7-0.3,1.3-0.5,2-0.7l0.1,0l0.3,1.1l-0.1,0C25.6,46.8,25,47.1,24.4,47.3z M34.7,47c-0.7-0.2-1.3-0.4-2-0.6l0.2-1.1c0.7,0.1,1.5,0.3,2.2,0.6L34.7,47z M28.4,46.2l-0.1-1.1c0.8-0.1,1.5-0.1,2.3-0.1l0,1.1 C29.9,46.1,29.1,46.2,28.4,46.2z M57.4,43.6l-1.1-0.1c0.1-0.7,0.1-1.4,0.1-2.1l1.1,0C57.5,42.1,57.5,42.8,57.4,43.6z M56.5,39.1 c0-0.7-0.1-1.5-0.2-2.1l1.1-0.2c0.1,0.7,0.2,1.5,0.3,2.3L56.5,39.1z M55.2,36.3c-0.8,0-1.6-0.1-2.3-0.3l0.3-1.1 c0.6,0.2,1.3,0.2,2.1,0.2L55.2,36.3z M57.5,36.1L57.4,35c0.7-0.1,1.4-0.3,2.1-0.5l0.3,1.1C59,35.8,58.2,36,57.5,36.1z M55.7,35 c-0.2-0.6-0.4-1.1-0.7-1.7L54.8,33l1-0.5l0.1,0.3c0.3,0.6,0.6,1.2,0.8,1.8L55.7,35z M50.7,34.9c-0.1-0.1-0.2-0.2-0.3-0.3 c-0.4-0.5-0.6-1.1-0.6-1.7c0-0.2,0-0.3,0-0.5l1.1,0.2c0,0.1,0,0.2,0,0.3c0,0.4,0.1,0.7,0.3,1c0.1,0.1,0.1,0.1,0.2,0.2L50.7,34.9z M61.9,34.8l-0.4-1c0.2-0.1,0.4-0.2,0.6-0.3c0.5-0.2,0.9-0.4,1.4-0.6l0.5,1c-0.5,0.2-0.9,0.4-1.4,0.6 C62.3,34.6,62.1,34.7,61.9,34.8z M65.9,32.9l-0.5-1c0.7-0.3,1.3-0.7,2-1l0.5,1C67.2,32.2,66.6,32.6,65.9,32.9z M53.6,31.6 c-0.2-0.1-0.4-0.2-0.5-0.2c-0.3-0.1-0.7-0.1-1.1,0.1l-0.4-1c0.6-0.2,1.2-0.3,1.8-0.1c0.3,0.1,0.6,0.2,0.9,0.4L53.6,31.6z M69.8,30.9l-0.5-1l1.9-1l0.5,1L69.8,30.9z M73.7,28.8l-0.5-1c0.7-0.3,1.3-0.7,2-1l0.5,1C75,28.2,74.4,28.5,73.7,28.8z M77.7,27 l-0.4-1c0.7-0.3,1.4-0.6,2.1-0.8l0.4,1C79,26.4,78.3,26.7,77.7,27z M81.7,25.4l-0.3-1.1c0.7-0.2,1.5-0.4,2.2-0.6l0.3,1.1 C83.2,25,82.4,25.2,81.7,25.4z"></path></g><g id="change1_1"><path fill="#8428fa" d="M86.1,24.5l-0.2-1.1c0.4-0.1,0.8-0.1,1.1-0.1l0.1,1.1C86.8,24.4,86.4,24.4,86.1,24.5z"></path></g></g></svg>
```


---

# 6. WHAT IS NOT IN THIS FILE (losses vs. the full project)

- **PNG assets** — the mosaic backgrounds (title-slide panels, corner clusters, confetti strip, yellow banner), all solid-shape PNGs (circles, triangles, semicircle stacks, petals, starburst, checkerboard, fan-lines), the 17 sector/stakeholder line icons, speech bubbles, hand-drawn arrows, and the world map. These are raster images and cannot live in Markdown. Compose shape clusters from CSS/SVG primitives per the Shape rules in §1, or pull the PNGs from the design-system project ("Open Supply Hub Design System") / the original decks.
- **Font binaries** (woff2) — use the Google Fonts link in §2 instead; zero fidelity loss.
- **Compiled component bundle & Design System tab cards** — tooling-specific; the JSX sources in §3 are the portable equivalent.
- **The 13-slide deck template** — its layouts are fully represented by §4.
- **Source decks & brand PDFs** — referenced in §1 Sources; not embedded.

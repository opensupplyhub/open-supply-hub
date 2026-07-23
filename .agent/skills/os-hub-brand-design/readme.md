# Open Supply Hub Design System

> **Repo copy note:** to keep the repository light, the heavy source binaries referenced under `uploads/` (source PPTX decks, brand-guide PDF pages) and the image renders under `extracted/` are **not** included here — only the markdown extracts and the External Comms Style Guide are. Everything needed to produce branded output (tokens, fonts, assets, components, slide layouts, guidelines) is present. The full source bundle is documented on the Confluence "Common Dev Brain -- Skills" page; ask Tyler Heath for the original archive if you need the raw decks.

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

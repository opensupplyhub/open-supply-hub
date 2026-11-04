# OS Hub Product App UI — how the real platform implements the brand

The brand system in this skill was built from decks and brand guidelines. The **product app** (opensupplyhub.org, `src/react/` in the open-supply-hub repo) implements the same brand with its own libraries and files. **For product UI work, the code below is the source of truth — read the actual files; this page is a map, and a snapshot as of July 2026.**

## Libraries

| Library | Version | Role |
|---------|---------|------|
| `@material-ui/core` | 3.1.0 | UI component library (old MUI v3 — uses `createMuiTheme`, JSS `withStyles`, NOT modern `@mui/material` APIs) |
| `@material-ui/icons` | 3.0.1 | Icons |
| `typeface-darker-grotesque` | 1.1.13 | Brand font, loaded via npm import (`import 'typeface-darker-grotesque';` in App.jsx) |
| `sass` | 1.101.0 | Header/footer styles only |

## Where design lives (repo-relative paths)

- `src/react/src/App.jsx` — the MUI theme (`createMuiTheme`): palette, typography, custom breakpoints (sm 700 / md 900 / lg 1280 / xl 1920). Theme colors can be **overridden at runtime** by embedded-map (white-label) config — `config.color` / `config.font` — so never hardcode assumptions that primary is always purple in embed contexts.
- `src/react/src/util/constants.jsx` — brand constants:
  - `OARColor = '#8428FA'` (primary purple)
  - `OARActionColor = '#FFCF3F'` (action/CTA yellow)
  - `OARSecondaryColor = '#FFA6D0'` (secondary pink)
- `src/react/src/util/COLOURS.js` — the full named palette (~85 colors). Always import from here rather than hardcoding hex values. Brand-aligned anchors: `PURPLE '#8428FA'`, `LIGHT_GREY '#F9F7F7'` (= brand cream), `NEAR_BLACK '#0D1128'` (= brand off-black), `NAVIGATION '#FCCF3F'`, `WHITE '#FFF'`.
- `src/react/src/index.css` — global baseline; sets `font-family: 'Darker Grotesque', sans-serif` on body and form elements.
- `src/react/src/App.css` — ~650 lines of utility/component classes.
- `src/react/src/styles/css/header.scss` + `footer.scss` — Sass with their own variables: `$purple-500 #8428FA`, `$pink-500 #FFA6D0`, `$yellow-500 #FCCF3F`, `$white-500 #F9F7F7`, `$grey-500 #0D1128`, `$ff-main 'Darker Grotesque'`, base grid `$gtr = 16px`.
- `src/react/src/components/ProductionLocation/` — the PL-page redesign uses theme-aware `styles.js` files per component (plus `commonStyles.js`), pulling from `theme.palette` and `COLOURS` (e.g. `CLAIMED_CHIP_BG`, `CROWDSOURCED_CHIP_BG/_TEXT`).

## Theme snapshot (App.jsx)

```javascript
palette: {
  primary:   { main: config.color || OARColor },      // #8428FA unless white-labeled
  secondary: { main: OARSecondaryColor },              // #FFA6D0
  action:    { main: OARActionColor,                   // #FFCF3F
               contrastText: 'rgba(0, 0, 0, 0.87)' },
  background:{ grey: COLOURS.LIGHT_GREY, white: COLOURS.WHITE },
},
typography: {
  fontFamily: config.font,                             // 'Darker Grotesque', sans-serif by default
  fontWeightSemiBold: 600, fontWeightSemiBoldPlus: 700,
  fontWeightBold: 800, fontWeightExtraBold: 900,
}
```

## Gotchas

- **Two different yellows exist in the app**: `OARActionColor '#FFCF3F'` (constants.jsx, MUI theme) vs `NAVIGATION` / `$yellow-500 '#FCCF3F'` (COLOURS.js, SCSS). They are one character apart and both in active use — match whichever the surrounding code uses; don't "fix" one to the other without a ticket.
- MUI v3 idioms only: `createMuiTheme`, `withStyles`/JSS. Modern `sx` props, `styled()`, or `@mui/*` imports will not work.
- App font weights run 400/600/700/800/900 via the npm typeface package; the collateral system's "headings Black at 92% line-height" is a deck convention, not an app rule.
- White-label/embedded maps can swap primary color and font at runtime — use `theme.palette.primary.main`, never a hardcoded purple, in components that can render inside embeds.

## Which system do I use?

- Decks, one-pagers, explainer HTML, prototypes, comms → the rest of this skill (`tokens/`, `assets/`, `slides/`).
- Changes to the actual platform UI → the files above, plus the repo's own conventions (PropTypes, JSS, Redux patterns). This page orients you; the code decides.

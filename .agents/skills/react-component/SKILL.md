---
name: react-component
description: Create a new React component in the Open Supply Hub frontend following project conventions. Use when the user asks to build, add, or scaffold a new UI component, sub-component, or feature area in src/react/src/components/.
---

# React Component Creation (OSH)

Reference implementation: `src/react/src/components/ProductionLocation/`

---

## Directory Layout

Every component lives in its **own PascalCase folder**. Files inside the folder are **camelCase**. No `index.js` barrel files.

```
ComponentName/
├── ComponentName.jsx   # required — component + PropTypes + default export
├── styles.js           # required — JSS style factory
├── constants.js        # when the component has static strings, URLs, or enums
├── utils.js            # when the component needs helper functions
├── hooks.js            # when the component has custom hooks
└── SubComponent/       # nest child components the same way
    ├── SubComponent.jsx
    └── styles.js
```

Create only the files you need. `styles.js` is always required. Others are optional.

---

## Component File — `ComponentName.jsx`

### Arrow function — required for all components

```jsx
import React, { useState } from 'react';
import { string, object, func } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';

import componentStyles from './styles';
import { SOME_CONSTANT } from './constants';

const ComponentName = ({ classes, label, onClick }) => {
    const [active, setActive] = useState(false);

    const handleClick = () => setActive(prev => !prev);

    return (
        <div className={classes.root} onClick={handleClick}>
            <span className={classes.label}>{label}</span>
        </div>
    );
};

ComponentName.propTypes = {
    classes: object.isRequired,
    label: string.isRequired,
    onClick: func.isRequired,
};

ComponentName.defaultProps = {
    // optional defaults here
};

export default withStyles(componentStyles)(ComponentName);
```

### Component with Redux

Add `connect` at the bottom, composed outside-in. `mapStateToProps` and `mapDispatchToProps` are inline functions in the same file:

```jsx
import { connect } from 'react-redux';
import { withRouter } from 'react-router-dom';
import { withStyles } from '@material-ui/core/styles';
import { someAction } from '../../../actions/someActions';
import { getSomeSelector } from '../../../selectors/someSelectors';

// ... component definition ...

const mapStateToProps = ({ someSlice, featureFlags }) => ({
    data: getSomeSelector(someSlice),
});

const mapDispatchToProps = dispatch => ({
    doSomething: () => dispatch(someAction()),
});

export default withRouter(
    connect(mapStateToProps, mapDispatchToProps)(
        withStyles(componentStyles)(ComponentName),
    ),
);
```

---

## `styles.js`

```js
import COLOURS from '../../../util/COLOURS';
import { getTypographyStyles } from '../../../util/typographyStyles';

export default theme => {
    const typography = getTypographyStyles(theme);
    const spacing = theme.spacing.unit ?? 8;

    return Object.freeze({
        root: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            padding: `${spacing * 2}px`,
        }),
        label: Object.freeze({
            ...typography.formLabel,
            color: COLOURS.NEAR_BLACK,
        }),
        // responsive example:
        container: {
            width: '100%',
            [theme.breakpoints.down('sm')]: {
                flexDirection: 'column',
            },
        },
    });
};
```

**Rules:**
- Always `export default theme => ({ ... })` — a factory function, not a plain object
- Wrap each style object in `Object.freeze()`; skip freeze only on objects that contain theme breakpoints (they must remain mutable)
- Use `COLOURS` from `../../../../util/COLOURS` (adjust depth to actual location)
- Use `theme.spacing.unit` for spacing; use `theme.palette` for colors from the theme
- Use `theme.breakpoints.down('sm')` for responsive rules inside style objects

---

## `constants.js`

For static values only — strings, URLs, enums, config. No logic.

```js
export const LABEL_TEXT = 'Some UI label';

export const LEARN_MORE_URL = 'https://info.opensupplyhub.org/...';

export const STATUS = Object.freeze({
    active: 'active',
    inactive: 'inactive',
});
```

---

## `utils.js`

For pure functions that derive or transform data.

```js
import { STATUS } from './constants';

export const getStatusLabel = status =>
    status === STATUS.active ? 'Active' : 'Inactive';

export const filterByStatus = (items, status) =>
    items.filter(item => item.status === status);
```

---

## `hooks.js`

For custom hooks used by this component or its children.

```js
import { useState, useEffect } from 'react';

export const useToggle = (initial = false) => {
    const [value, setValue] = useState(initial);
    const toggle = () => setValue(prev => !prev);
    return [value, toggle];
};
```

---

## ES6 Rules — Always Apply

- **Arrow functions** for component definitions, event handlers, and utilities — **required, no exceptions**
- **Destructuring** in function parameters: `({ classes, label, onClick })`
- **Spread** for extending styles or props: `{ ...commonStyles, color: 'red' }`
- **Template literals** instead of string concatenation
- **`const`** / **`let`** — never `var`
- **Named exports** for constants and utils; **default export** only for the component itself
- **No `.bind(this)`** — use arrow functions in render or class property syntax (but no classes)

---

## Naming Conventions

| Item | Convention | Example |
|---|---|---|
| Component folder | PascalCase | `OsIdBadge/` |
| Component file | PascalCase + `.jsx` | `OsIdBadge.jsx` |
| Sub-component folder | PascalCase | `MetaContributor/` |
| Utility files | camelCase + `.js` | `styles.js`, `constants.js`, `utils.js`, `hooks.js` |
| Exported constants | UPPER_SNAKE_CASE | `OS_ID_TOOLTIP_TEXT` |
| Exported enums | UPPER_SNAKE_CASE object | `VARIANT`, `STATUS` |
| Hook functions | `use` prefix + camelCase | `useToggle`, `useScrollToSection` |

---

## What NOT to Do

- **No class components** — `extends Component` is not used in new code
- **No `function` declarations for components** — always use `const ComponentName = (...) => { ... }`
- **No `makeStyles`** — the app uses `withStyles` (MUI v3 API)
- **No `index.js` barrel files** — import the full path: `../../OsIdBadge/OsIdBadge`
- **No inline styles** except for truly dynamic single-use values (e.g. `style={{ width: computed }}`)
- **No PropTypes in separate files** — always inline after the component definition
- **No logic in `constants.js`** — functions belong in `utils.js`
- **No hardcoded hex values in styles** — use `COLOURS` tokens or `theme.palette`

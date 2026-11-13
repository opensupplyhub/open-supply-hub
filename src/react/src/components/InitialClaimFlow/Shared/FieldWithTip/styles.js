const FIELD_COLUMN = 'minmax(0, 528px)';

// Widths match the step wrappers this replaces (`fieldContainer` in the
// Contact step, `formFieldContainer` in the Business step). Those capped the
// field at 528px and lifted the cap under `down('md')`, which covers
// everything below `lg`. So below `lg` the field, and the tip under it, are
// full width with no cap, and from `lg` up the field column is capped at
// 528px.
const styles = theme =>
    Object.freeze({
        root: Object.freeze({
            width: '100%',
            position: 'relative',
            // Wide screens: the field in the first column, its tip in the
            // second, same width, inside the form card.
            [theme.breakpoints.up('lg')]: {
                display: 'grid',
                gridTemplateColumns: `${FIELD_COLUMN} ${FIELD_COLUMN}`,
                columnGap: '24px',
            },
        }),
        field: Object.freeze({
            [theme.breakpoints.up('lg')]: {
                gridColumn: 1,
            },
        }),
        tip: Object.freeze({
            margin: '8px 0 12px 0',
            // Second row is the control, so the tip is level with it.
            [theme.breakpoints.up('lg')]: {
                gridColumn: 2,
                gridRow: 2,
                alignSelf: 'start',
                margin: 0,
            },
        }),
    });

export default styles;

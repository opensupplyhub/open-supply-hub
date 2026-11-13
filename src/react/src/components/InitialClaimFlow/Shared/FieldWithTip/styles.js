const FIELD_COLUMN = 'minmax(0, 528px)';

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

import COLOURS from '../../../../../../util/COLOURS';

export default theme =>
    Object.freeze({
        anonymizedSection: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            marginBottom: '16px',
        }),
        anonymizedList: Object.freeze({
            display: 'flex',
            flexDirection: 'column',
            gap: '8px',
        }),
        anonymizedType: Object.freeze({
            fontSize: '1rem',
            color: COLOURS.NEAR_BLACK,
            lineHeight: 1.8,
        }),
        anonymizedIcon: Object.freeze({
            fontSize: '1.5rem',
            color: theme.palette.text.primary,
            flexShrink: 0,
        }),
        sectionLabel: Object.freeze({
            fontWeight: 700,
            fontSize: '1.4rem',
            lineHeight: 1.3,
            color: COLOURS.NEAR_BLACK,
            letterSpacing: '0.5px',
            marginLeft: '10px',
        }),
    });

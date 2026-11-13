import COLOURS from '../../../util/COLOURS';

export default () =>
    Object.freeze({
        chip: Object.freeze({
            display: 'inline-flex',
            alignItems: 'center',
            padding: '3px 10px',
            borderRadius: 9999,
            fontSize: '0.6875rem',
            fontWeight: 700,
            lineHeight: 1.2,
            letterSpacing: '0.04em',
            textTransform: 'uppercase',
            whiteSpace: 'nowrap',
            flexShrink: 0,
            color: COLOURS.WHITE,
            backgroundImage: `linear-gradient(to right, ${COLOURS.PURPLE_GRADIENT_FROM}, ${COLOURS.PINK_GRADIENT_TO})`,
        }),
    });

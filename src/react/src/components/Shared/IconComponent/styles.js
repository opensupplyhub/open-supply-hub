import COLOURS from '../../../util/COLOURS';

export default theme =>
    Object.freeze({
        popper: Object.freeze({
            opacity: 1,
        }),
        defaultTooltipIcon: Object.freeze({
            display: 'inline-flex',
        }),
        tooltip: Object.freeze({
            fontSize: '0.875rem',
            backgroundColor: COLOURS.WHITE,
            color: COLOURS.BLACK,
            border: `1px solid ${COLOURS.GREY}`,
            padding: `${theme.spacing.unit * 1.5}px`,
            maxWidth: '300px',
        }),
        tooltipVisible: Object.freeze({
            opacity: '1 !important',
        }),
        icon: Object.freeze({
            fontSize: '1rem',
            color: COLOURS.DARK_GREY,
            cursor: 'pointer',
        }),
    });

import COLOURS from '../../../../util/COLOURS';

const styles = theme =>
    Object.freeze({
        box: Object.freeze({
            boxSizing: 'border-box',
            width: '100%',
            backgroundColor: COLOURS.WHITE,
            border: `2px solid ${COLOURS.MATERIAL_GREEN}`,
            padding: theme.spacing.unit * 1.5,
            margin: '8px 0 12px 0',
        }),
        title: Object.freeze({
            fontSize: '18px',
            fontWeight: theme.typography.fontWeightSemiBold,
        }),
        detail: Object.freeze({
            fontSize: '16px',
        }),
        delay: Object.freeze({
            fontSize: '16px',
            color: COLOURS.DARK_GREY,
        }),
    });

export default styles;
